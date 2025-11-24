from collections import defaultdict

import pandas as pd
from django.core.management.base import BaseCommand
from django.db.models import CharField, F, Func, Value
from django.db.models.functions import Round

from elec.models import ElecMeterReading


class Command(BaseCommand):
    help = "Delete duplicate charge points"

    def handle(self, *args, **options):
        readings = (
            ElecMeterReading.objects.select_related("cpo", "application", "meter", "meter__charge_point")
            .filter(application__year=2024)
            .order_by(
                "cpo__name",
                "meter__charge_point__charge_point_id",
                "application__year",
                "application__quarter",
                "reading_date",
            )
            .annotate(
                round_extracted_energy=Round(F("extracted_energy"), 2),
                round_energy_used_since_last_reading=Round(F("energy_used_since_last_reading"), 2),
                reading_date_str=Func(
                    F("reading_date"), Value("%Y-%m-%d"), function="DATE_FORMAT", output_field=CharField()
                ),
            )
        )

        readings = readings.values(
            "cpo__name",
            "meter__charge_point__charge_point_id",
            "application__year",
            "application__quarter",
            "reading_date_str",
            "round_extracted_energy",
            "round_energy_used_since_last_reading",
            "days_since_last_reading",
            "meter__initial_index",
            "meter__initial_index_date",
        )

        df = pd.DataFrame(list(readings))
        df.to_csv("/tmp/readings.csv", index=False)

        by_cpo = defaultdict(lambda: defaultdict(list))
        for reading in readings:
            by_cpo[reading["cpo__name"]][reading["meter__charge_point__charge_point_id"]].append(reading)

        total_excess = 0
        skipped = 0
        for cpo, charge_points in by_cpo.items():
            total_cpo_excess = 0
            for readings in charge_points.values():
                last = None
                for reading in sorted(readings, key=lambda x: x["reading_date_str"]):
                    if last is None:
                        last = reading
                        continue
                    previous_energy = last["round_extracted_energy"]
                    # la ligne ci dessous permet de prendre en compte le relevé initial associé au compteur
                    # previous_energy = last["round_extracted_energy"] if last else reading["meter__initial_index"]
                    if previous_energy is None:
                        skipped += 1
                        continue
                    computed_delta = reading["round_energy_used_since_last_reading"]
                    expected_delta = (reading["round_extracted_energy"] or 0) - previous_energy
                    surplus = computed_delta - expected_delta
                    total_cpo_excess += surplus
                    last = reading

            if abs(total_cpo_excess) > 1:
                total_excess += total_cpo_excess
                print(f"> {cpo}: {round(total_cpo_excess * 0.25 / 1000, 1)} MWh")

        print(f"Soit un total de {round(total_excess * 0.25 / 1000, 1)} MWh")
