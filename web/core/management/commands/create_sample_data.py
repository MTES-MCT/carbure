from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Crée les données de démonstration d'une app"

    def add_arguments(self, parser):
        parser.add_argument("app_name", nargs="?", type=str)
        parser.add_argument("--reset", action="store_true", help="Recrée la base configurée avant de générer les données")
        # parser.add_argument("--scope", type=str)  # basic / complete

    def handle(self, *args, **kwargs):
        app_name = kwargs["app_name"]

        if kwargs["reset"]:
            self._reset_database()

        if app_name is None:
            for app_config in apps.get_app_configs():
                self._create_sample_data(app_config.name)
            return

        self._create_sample_data(app_name, report_missing=True)

    def _reset_database(self):
        try:
            confirmation = input("Supprimer la base de données actuelle et toutes ses données ? [oui/non] ")
        except EOFError:
            raise CommandError("Réinitialisation annulée") from None
        if confirmation.strip().lower() != "oui":
            raise CommandError("Réinitialisation annulée.")

        name = connection.settings_dict["NAME"].replace("`", "``")
        connection.close()
        with connection._nodb_cursor() as cursor:
            cursor.execute(f"DROP DATABASE `{name}`")
            cursor.execute(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4")
        call_command("migrate")

    def _create_sample_data(self, app_name, report_missing=False):
        try:
            module = __import__(f"{app_name}.factories.sample_data", fromlist=["create_sample_data"])
            with transaction.atomic():
                self.stdout.write(f"> Création des données pour l'app '{app_name}'...")
                module.create_sample_data()
        except (ImportError, AttributeError) as e:
            if report_missing:
                print(e)
                self.stderr.write(f"L'app '{app_name}' n'a pas de create_sample_data()")
        else:
            self.stdout.write(f"> Données créées pour l'app '{app_name}'")
