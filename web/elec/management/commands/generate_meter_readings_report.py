import json
from collections import defaultdict

import pandas as pd
from django.core.management.base import BaseCommand
from django.db.models import CharField, F, Func, Value
from django.db.models.functions import Concat, Round

from elec.models import ElecMeterReading
from transactions.models.year_config import YearConfig


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

    def handle(self, *args, **options):
        year = options.get("year")
        log = options.get("log")
        csv = options.get("csv")

        year_configs = YearConfig.objects.all()
        enr_ratio_per_year = {c.year: c.renewable_share for c in year_configs}

        readings = (
            ElecMeterReading.objects.select_related("cpo", "application", "meter", "meter__charge_point")
            .filter(meter__charge_point__is_deleted=False)
            .order_by(
                "cpo__name",
                "meter__charge_point__charge_point_id",
                "application__year",
                "application__quarter",
                "meter_id",
                "reading_date",
            )
            .annotate(
                cpo_name=F("cpo__name"),
                charge_point_id=F("meter__charge_point__charge_point_id"),
                current_meter=Concat(F("meter_id"), Value("-"), F("meter__mid_certificate"), output_field=CharField()),
                year=F("application__year"),
                quarter=F("application__quarter"),
                current_index=Round(F("extracted_energy"), 2),
                current_date=Func(F("reading_date"), Value("%Y-%m-%d"), function="DATE_FORMAT", output_field=CharField()),
                saved_index_delta=Round(F("energy_used_since_last_reading"), 2),
                saved_renewable=Round(F("renewable_energy"), 2),
                initial_index=F("meter__initial_index"),
                initial_index_date=F("meter__initial_index_date"),
            )
        )

        readings = readings.values(
            "cpo_name",
            "charge_point_id",
            "current_meter",
            "year",
            "quarter",
            "current_index",
            "current_date",
            "initial_index",
            "initial_index_date",
            "saved_index_delta",
            "saved_renewable",
        )

        if csv:
            df = pd.DataFrame(list(readings))
            df.to_csv("/tmp/readings.csv", index=False)

        by_cpo = defaultdict(lambda: defaultdict(list))
        for reading in readings:
            by_cpo[reading["cpo_name"]][reading["charge_point_id"]].append(reading)

        report = {}
        total_surplus = 0

        for cpo, charge_points in by_cpo.items():
            total_cpo_surplus = 0

            for _charge_point, readings in charge_points.items():
                previous = None
                for reading in readings:
                    previous_energy = None

                    # grab the last index from the previous reading of the current meter
                    # otherwise directly use the meter initial index
                    if previous is not None and previous["current_meter"] == reading["current_meter"]:
                        previous_energy = previous["current_index"]
                    else:
                        previous_energy = reading["initial_index"]

                    current_date = reading["current_date"]
                    current_index = reading["current_index"]
                    saved_renewable = reading["saved_renewable"]
                    saved_index_delta = reading["saved_index_delta"]

                    # for old readings when we didn't compute energy_used_since_last_reading yet
                    if round(saved_index_delta) == 0:
                        enr_ratio = enr_ratio_per_year[reading["year"]] / 100
                        saved_index_delta = saved_renewable / enr_ratio
                    else:
                        enr_ratio = saved_renewable / saved_index_delta

                    expected_index_delta = round(current_index - previous_energy, 2)
                    surplus = saved_index_delta - expected_index_delta

                    if year is None or current_date.startswith(str(year)):
                        total_cpo_surplus += surplus * enr_ratio

                    previous = reading

            if total_cpo_surplus != 0:
                total_surplus += total_cpo_surplus
                report[cpo] = round(total_cpo_surplus, 3)

        if log:
            df = pd.DataFrame(report.items(), columns=["Aménageur", "Surplus (kWh)"])
            pd.options.display.float_format = "{:,.3f}".format
            print(df.to_string(index=False))
            print(f"Soit un total de {round(total_surplus / 1000, 1):,} MWh\n")

        return json.dumps(report)
