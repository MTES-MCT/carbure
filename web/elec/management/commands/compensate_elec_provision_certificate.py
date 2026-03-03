import json
from datetime import date

from django.core.management.base import BaseCommand
from django.db.models import CharField, Sum
from django.db.models.expressions import F, Value
from django.db.models.functions import Cast, Concat, Round

from elec.models import ElecProvisionCertificate
from elec.models.elec_meter_reading import ElecMeterReading
from transactions.models import YearConfig


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
            "--log",
            action="store_true",
            default=True,
            help="Log the compensation",
        )

    def handle(self, *args, **options):
        enr_ratio = options["enr_ratio"]
        if options["log"]:
            print(f" -- Running with ENR ratio = {enr_ratio}%.")

        today = date.today()
        last_year = today.year - 1
        new_enr_ratio = enr_ratio / 100  # 25 -> 0.25

        meter_readings = (
            ElecMeterReading.extended_objects.prefetch_related("application", "cpo")
            .filter(application__year=last_year)
            .values(
                "cpo__id",
                "cpo__name",
                "operating_unit",
                "application__year",
                "application__quarter",
            )
            .annotate(
                total_energy_used=Round(Sum((F("current_index") - F("prev_index")) * F("enr_ratio")), 3),
                recalculated_energy_amount=Round(Sum((F("current_index") - F("prev_index")) * new_enr_ratio), 3),
            )
            .order_by("cpo__name", "operating_unit", "application_id")
        )

        certificates_already_created = (
            ElecProvisionCertificate.objects.filter(
                year=last_year,
                source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            )
            .values("cpo_id", "quarter", "year", "operating_unit")
            .annotate(
                key=Concat(
                    Cast(F("cpo_id"), output_field=CharField()),
                    Value("-"),
                    Cast(F("quarter"), output_field=CharField()),
                    Value("-"),
                    Cast(F("year"), output_field=CharField()),
                    Value("-"),
                    F("operating_unit"),
                )
            )
            .values_list("key", flat=True)
        )

        elec_provision_certificates = []

        for meter_reading in meter_readings:
            # Delta in KWH (value retrieved from the meter readings)
            delta_in_kwh = float(meter_reading["recalculated_energy_amount"] - meter_reading["total_energy_used"])
            delta_in_mwh = round(delta_in_kwh / 1000, 2)

            # Unique key to check if the certificate has already been created.
            key = (
                f"{meter_reading['cpo__id']}-{meter_reading['application__quarter']}"
                f"-{meter_reading['application__year']}-{meter_reading['operating_unit']}"
            )

            # Check if there is a delta between the energy declared, and the energy calculated by the new ENR ratio.
            # If there is a delta, and the certificate has not already been created, create a new certificate.
            if delta_in_mwh > 0 and key not in certificates_already_created:
                elec_provision_certificates.append(
                    ElecProvisionCertificate(
                        cpo_id=meter_reading["cpo__id"],
                        quarter=meter_reading["application__quarter"],
                        year=last_year,
                        operating_unit=meter_reading["operating_unit"],
                        energy_amount=delta_in_mwh,
                        source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
                    )
                )

        if options["apply"]:
            if elec_provision_certificates:
                ElecProvisionCertificate.objects.bulk_create(elec_provision_certificates, batch_size=10)
                if options["log"]:
                    print(f"Created {len(elec_provision_certificates)} new certificates")
            elif options["log"]:
                print("No new certificates to create")

            YearConfig.objects.filter(year=today.year).update(renewable_share=new_enr_ratio)

        # Return the result as a JSON object for the tests.
        result = [
            {
                "cpo_id": c.cpo_id,
                "quarter": c.quarter,
                "year": c.year,
                "operating_unit": c.operating_unit,
                "energy_amount": c.energy_amount,
                "source": c.source,
            }
            for c in elec_provision_certificates
        ]
        return json.dumps(result)
