from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Crée les données de démonstration d'une app"

    reference_fixtures = (
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
    )

    def add_arguments(self, parser):
        parser.add_argument("app_name", nargs="?", type=str)
        # parser.add_argument("--scope", type=str)  # basic / complete

    def handle(self, *args, **kwargs):
        app_name = kwargs["app_name"]
        self._load_reference_fixtures()

        if app_name is None:
            for app_config in apps.get_app_configs():
                self._create_sample_data(app_config.name)
            return

        self._create_sample_data(app_name, report_missing=True)

    def _load_reference_fixtures(self):
        self.stdout.write("> Chargement des référentiels biofuels, feedstocks et pays...")
        call_command("loaddata", *self.reference_fixtures, verbosity=0)

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
