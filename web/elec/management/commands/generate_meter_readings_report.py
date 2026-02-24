import json

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models.aggregates import Sum

from elec.models import ElecCertificateReadjustment, ElecMeterReading, ElecProvisionCertificate
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication


def _get_real_total_energy_declared(cpo_id):
    result = (
        ElecMeterReading.extended_objects.select_related("application")
        .filter(cpo_id=cpo_id, application__status=ElecMeterReadingApplication.ACCEPTED)
        .aggregate(Sum("renewable_energy"))
    )

    return result["renewable_energy__sum"] or 0


def _get_certificates_energy_amount(cpo_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT SUM(energy_amount) FROM elec_provision_certificate epc
            WHERE epc.cpo_id = %s AND epc.source = "METER_READINGS"
            """,
            [cpo_id],
        )
        result = cursor.fetchone()

        return result[0] * 1000 if result and result[0] is not None else 0


class Command(BaseCommand):
    help = "Generate a report for all the meter readings registered in Carbure"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            default=None,
            help="Year of meter readings to include in the report",
        )
        parser.add_argument(
            "--log",
            default=False,
            action="store_true",
            help="Print logs during execution",
        )
        parser.add_argument(
            "--csv",
            default=False,
            action="store_true",
            help="Store meter reading details in a CSV file at /tmp/readings.csv",
        )
        parser.add_argument(
            "--cpo",
            type=int,
            default=None,
            help="Cpo to filter readings",
        )
        parser.add_argument(
            "--apply",
            default=False,
            action="store_true",
            help="Create readjustments in the table elec_certificate_readjustment for each cpo",
        )

    def handle(self, *args, **options):
        log = options.get("log")
        csv = options.get("csv")
        cpo = options.get("cpo")
        apply_readjustments = options.get("apply")

        cpo_with_readings = ElecMeterReading.objects.select_related("cpo").values("cpo_id", "cpo__name")

        if cpo is not None:
            cpo_with_readings = cpo_with_readings.filter(cpo_id=cpo)

        cpo_with_readings = cpo_with_readings.distinct()

        report = {}
        total_surplus = 0

        for cpo in cpo_with_readings:
            total_meter_reading_energy = _get_real_total_energy_declared(cpo["cpo_id"])
            total_provision_certificate_energy = _get_certificates_energy_amount(cpo["cpo_id"])

            total_admin_error_readjustment_dict = ElecProvisionCertificate.objects.filter(
                cpo_id=cpo["cpo_id"], source=ElecProvisionCertificate.ADMIN_ERROR_COMPENSATION
            ).aggregate(Sum("energy_amount"))
            total_admin_error_readjustment = (
                total_admin_error_readjustment_dict.get("energy_amount__sum") or 0
            ) * 1000  # back to kWh to match meter reading energy values

            total_cpo_readjustment_dict = ElecCertificateReadjustment.objects.filter(
                cpo_id=cpo["cpo_id"], error_source=ElecCertificateReadjustment.METER_READINGS
            ).aggregate(Sum("energy_amount"))
            total_cpo_readjustment = (
                total_cpo_readjustment_dict.get("energy_amount__sum") or 0
            ) * 1000  # back to kWh to match meter reading energy values

            diff = (
                total_provision_certificate_energy
                - total_meter_reading_energy
                - total_cpo_readjustment
                + total_admin_error_readjustment
            )

            # if diff is more than 100 kWh, it's a significant difference
            if abs(diff) >= 100:
                total_surplus += diff
                report[cpo["cpo__name"]] = {
                    "certificats": total_provision_certificate_energy,
                    "real_energy_must_be_declared": total_meter_reading_energy,
                    "surplus": round(diff, 3),
                }

                # create a readjustment only if the cpo has a positive surplus
                if apply_readjustments and diff > 0:
                    ElecCertificateReadjustment.objects.create(
                        cpo_id=cpo["cpo_id"],
                        error_source=ElecCertificateReadjustment.METER_READINGS,
                        # back to MWh to match the energy_amount field
                        energy_amount=round(diff / 1000, 2),
                        reason="Différence entre l'énergie générée par certificats et l'énergie déclarée dans les relevés",
                    )

        if log:
            items = []
            for cpo, data in report.items():
                items.append(
                    {
                        "Aménageur": cpo,
                        "Energie générée par certificats (kWh)": data["certificats"],
                        "Énergie déclarée (kWh)": data["real_energy_must_be_declared"],
                        "Surplus (kWh)": data["surplus"],
                    }
                )

            sorted_items = sorted(items, key=lambda x: x["Surplus (kWh)"], reverse=True)
            df = pd.DataFrame(sorted_items)

            pd.options.display.float_format = "{:,.3f}".format
            print(df.to_string(index=False))
            print(f"Soit un total de {round(total_surplus / 1000, 1):,} MWh\n")

        if csv:
            arr = []
            for cpo, data in report.items():
                arr.append([cpo, data["certificats"], data["real_energy_must_be_declared"], data["surplus"]])
            df = pd.DataFrame(
                arr,
                columns=["Aménageur", "Energie générée par certificats (kWh)", "Énergie déclarée (kWh)", "Surplus (kWh)"],
            )
            df.to_csv("/tmp/readings.csv", index=False)

        return json.dumps({cpo: data["surplus"] for cpo, data in report.items()})
