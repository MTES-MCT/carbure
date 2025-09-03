from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crée les données de démonstration d'une app"

    def add_arguments(self, parser):
        parser.add_argument("app_name", type=str)
        # parser.add_argument("--scope", type=str)  # basic / complete

    def handle(self, *args, **kwargs):
        app_name = kwargs["app_name"]
        try:
            module = __import__(f"{app_name}.factories.sample_data", fromlist=["create_sample_data"])
            module.create_sample_data()
        except (ImportError, AttributeError):
            self.stderr.write(f"L'app '{app_name}' n'a pas de create_sample_data()")
        else:
            self.stdout.write(f"Données créées pour l'app '{app_name}'")
