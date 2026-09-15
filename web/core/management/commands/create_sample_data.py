from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Crée les données de démonstration d'une app"

    def add_arguments(self, parser):
        parser.add_argument("app_name", nargs="?", type=str)
        # parser.add_argument("--scope", type=str)  # basic / complete

    def handle(self, *args, **kwargs):
        app_name = kwargs["app_name"]

        if app_name is None:
            for app_config in apps.get_app_configs():
                self._create_sample_data(app_config.name)
            return

        self._create_sample_data(app_name, report_missing=True)

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
