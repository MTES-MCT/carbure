import pandas as pd
from django.core.management.base import BaseCommand
from django.db import connection

from elec.models import ElecMeterReading


def _get_real_total_energy_declared(cpo_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
	SUM((delta_table.current_index - delta_table.prev_index) * delta_table.ratio)
FROM
	(
	SELECT
			meter_id,
			ep.charge_point_id,
			ep.cpo_id,
			emr.renewable_energy,
			reading_date as current_index_date,
			extracted_energy as current_index,
			emra.year,
			emra.quarter,
			COALESCE(
				(SELECT
					emr_prev.extracted_energy
				FROM
					elec_meter_reading emr_prev
				WHERE
					emr_prev.meter_id = emr.meter_id
					AND emr_prev.id < emr.id
				ORDER BY
					emr_prev.id DESC
				LIMIT 1), em.initial_index) AS prev_index,
			COALESCE(
			# (emr.renewable_energy / emr.energy_used_since_last_reading),
			(SELECT renewable_share / 100 FROM year_config WHERE year=emra.year)) as ratio
		FROM
			elec_meter_reading emr
		INNER JOIN
			elec_meter em ON em.id = emr.meter_id
		INNER JOIN
			elec_charge_point ep ON ep.id = em.charge_point_id
		INNER JOIN
			elec_meter_reading_application emra ON emr.application_id = emra.id
		WHERE
			emr.cpo_id = %s AND ep.is_deleted = FALSE AND ep.is_article_2 = FALSE AND emra.status = "ACCEPTED"
		ORDER BY
			meter_id,
			current_index_date) as delta_table
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
            df = pd.DataFrame(items)

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
