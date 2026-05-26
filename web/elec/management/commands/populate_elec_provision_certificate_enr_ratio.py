from django.core.management.base import BaseCommand
from django.db import transaction

from elec.models import ElecProvisionCertificate
from transactions.models import YearConfig


class Command(BaseCommand):
    help = "Populate ElecProvisionCertificate.enr_ratio from YearConfig based on certificate year"

    # python web/manage.py populate_elec_provision_certificate_enr_ratio --apply
    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Apply changes to database",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        year_configs = YearConfig.objects.values("year", "renewable_share")
        enr_ratio_by_year = {config["year"]: config["renewable_share"] / 100 for config in year_configs}

        certificates = ElecProvisionCertificate.objects.all().only("id", "year", "enr_ratio").filter(enr_ratio__isnull=True)
        certificates_to_update = []
        missing_years = set()

        for certificate in certificates:
            enr_ratio = enr_ratio_by_year.get(certificate.year)
            if enr_ratio is None:
                missing_years.add(certificate.year)
                continue

            if certificate.enr_ratio != enr_ratio:
                certificate.enr_ratio = enr_ratio
                certificates_to_update.append(certificate)

        if missing_years:
            self.stdout.write(
                self.style.WARNING(
                    "No YearConfig found for years: " + ", ".join(str(year) for year in sorted(missing_years))
                )
            )

        self.stdout.write(f"Certificates to update: {len(certificates_to_update)}")

        if options["apply"]:
            ElecProvisionCertificate.objects.bulk_update(certificates_to_update, ["enr_ratio"], batch_size=1000)
            self.stdout.write(self.style.SUCCESS("Update applied"))
        else:
            self.stdout.write(self.style.WARNING("Dry run only. Use --apply to persist changes."))
