import pandas as pd
from django.core.management.base import BaseCommand
from django.db import connection

from elec.models import ElecMeterReading


# mettre à jour avec la vue elec_meter_reading_virtual
def _get_real_total_energy_declared(cpo_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT SUM((current_index - prev_index) * enr_ratio)
            FROM elec_meter_reading_virtual emrv
            INNER JOIN elec_meter_reading_application emra
            ON emra.id = emrv.application_id
            WHERE emrv.cpo_id = %s AND emra.status = "ACCEPTED"
        """,
            [cpo_id],
        )
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0


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

    def handle(self, *args, **options):
        log = options.get("log")
        csv = options.get("csv")
        cpo = options.get("cpo")

        cpo_with_readings = ElecMeterReading.objects.select_related("cpo").values("cpo_id", "cpo__name")

        if cpo is not None:
            cpo_with_readings = cpo_with_readings.filter(cpo_id=cpo)

        cpo_with_readings = cpo_with_readings.distinct()

        report = {}
        total_surplus = 0
        for cpo in cpo_with_readings:
            real_total_energy_must_be_declared = _get_real_total_energy_declared(cpo["cpo_id"])
            total_renewable_energy_declared = _get_certificates_energy_amount(cpo["cpo_id"])
            diff = total_renewable_energy_declared - real_total_energy_must_be_declared

            if diff > 0.1 or diff < -0.1:
                total_surplus += diff
                report[cpo["cpo__name"]] = {
                    "certificats": total_renewable_energy_declared,
                    "real_energy_must_be_declared": real_total_energy_must_be_declared,
                    "surplus": round(diff, 3),
                }

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
