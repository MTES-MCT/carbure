from datetime import date

from django.core.management.base import BaseCommand

from elec.management.scripts import generate_compensate_elec_provision_certificate


class Command(BaseCommand):
    help = "Compensate elec provision certificate"

    def add_arguments(self, parser):
        parser.add_argument(
            "--percent",
            type=int,
            default=25,
            help="Percent to use (default = 25%)",
        )

    def handle(self, *args, **options):
        percent = options["percent"]
        self.stdout.write(f" -- Running with renewable_share = {percent}%.")
        today = date.today()
        last_year = today.year - 1
        generate_compensate_elec_provision_certificate(last_year, percent)
