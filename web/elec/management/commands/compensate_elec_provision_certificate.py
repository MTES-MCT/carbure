from django.core.management.base import BaseCommand

from elec.management.scripts import compensate_elec_provision_certificate


class Command(BaseCommand):
    help = "Compensate elec provision certificate"

    def add_arguments(self, parser):
        parser.add_argument(
            "--enr_ratio",
            type=int,
            help="Current ENR ratio",
            required=True,
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Apply the compensation",
        )
        parser.add_argument(
            "--store-file",
            action="store_true",
            default=False,
            help="Store the data used to create the certificates in a file",
        )
        parser.add_argument(
            "--log",
            action="store_true",
            default=False,
            help="Log the compensation",
        )

    def handle(self, *args, **options):
        enr_ratio = options["enr_ratio"]
        self.stdout.write(f" -- Running with ENR ratio = {enr_ratio}%.")

        compensate_elec_provision_certificate(enr_ratio, options["apply"], options["store_file"], options["log"])
