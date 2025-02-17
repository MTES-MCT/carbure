# Importer les modules
from django.core.management.base import BaseCommand

from elec.management.scripts import generate_compensate_elec_provision_certificate


class Command(BaseCommand):
    help = "Compensate elec provision certificate"

    def add_arguments(self, parser):
        parser.add_argument(
            "--percent",
            type=int,
            default=25,
            help="Pourcentage à utiliser (par défaut: 25)",
        )

    def handle(self, *args, **options):
        percent = options["percent"] == "true"

        if percent:
            self.stdout.write(" -- Running with percent.")
        else:
            self.stdout.write(" -- Executing with default .")

        generate_compensate_elec_provision_certificate()
        # self.stdout.write(f"Points de charge conservés : {ids_to_keep}")
        # self.stdout.write(f"Points de charge conservés : {len(ids_to_keep)}")
