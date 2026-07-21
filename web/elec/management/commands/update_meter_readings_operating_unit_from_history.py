from datetime import timezone

import pandas as pd
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import OuterRef, Subquery
from django.db.models.functions import TruncDate

from elec.models import ElecMeterReading


class Command(BaseCommand):
    # Command : python web/manage.py update_meter_readings_operating_unit_from_history --year 2025 --apply
    help = "Compare operating_unit from meter readings with charge point history and optionally update mismatches."

    def add_arguments(self, parser):
        parser.add_argument(
            "--cpo",
            type=int,
            default=None,
            help="Filter by CPO id",
        )
        parser.add_argument(
            "--year",
            type=int,
            default=None,
            help="Filter by meter reading application year",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Apply operating_unit updates",
        )

    def handle(self, *args, **options):
        cpo_id = options["cpo"]
        year = options["year"]
        apply_updates = options["apply"]

        ElecChargePointHistory = apps.get_model("elec", "ElecChargePointHistory")
        previous_history = (
            ElecChargePointHistory.objects.annotate(history_day=TruncDate("history_date", tzinfo=timezone.utc))
            .filter(
                id=OuterRef("meter__charge_point_id"),
                history_day__lte=OuterRef("reading_date"),
            )
            .order_by("-history_date", "-history_id")
        )

        readings = (
            ElecMeterReading.objects.select_related("cpo", "application", "meter__charge_point")
            .filter(
                meter__isnull=False,
                meter__charge_point__isnull=False,
            )
            .annotate(
                previous_charge_point_id=Subquery(previous_history.values("charge_point_id")[:1]),
                previous_history_date=Subquery(previous_history.values("history_date")[:1]),
            )
            .exclude(previous_charge_point_id__isnull=True)
        )
        if cpo_id is not None:
            readings = readings.filter(cpo_id=cpo_id)
        if year is not None:
            readings = readings.filter(application__year=year)

        mismatches = []
        readings_to_update = []

        for reading in readings.iterator(chunk_size=1000):
            expected_operating_unit = reading.previous_charge_point_id[:5]
            current_operating_unit = reading.operating_unit

            if current_operating_unit == expected_operating_unit:
                continue

            mismatches.append(
                {
                    "reading_id": reading.id,
                    "cpo_id": reading.cpo_id,
                    "cpo_name": reading.cpo.name if reading.cpo else "",
                    "year": reading.application.year if reading.application else None,
                    "quarter": reading.application.quarter if reading.application else None,
                    "current_operating_unit": current_operating_unit,
                    "expected_operating_unit": expected_operating_unit,
                }
            )

            if apply_updates:
                reading.operating_unit = expected_operating_unit
                readings_to_update.append(reading)

        if mismatches:
            df = pd.DataFrame(mismatches)
            grouped_df = (
                df.groupby(
                    [
                        "cpo_id",
                        "cpo_name",
                        "year",
                        "quarter",
                        "current_operating_unit",
                        "expected_operating_unit",
                    ],
                    dropna=False,
                )
                .size()
                .reset_index(name="count")
                .sort_values(["cpo_name", "year", "quarter", "current_operating_unit", "expected_operating_unit"])
            )
            self.stdout.write(grouped_df.to_string(index=False))
        else:
            self.stdout.write("No operating_unit mismatch found.")

        self.stdout.write(f"Mismatches found: {len(mismatches)}")

        if apply_updates:
            if readings_to_update:
                ElecMeterReading.objects.bulk_update(readings_to_update, ["operating_unit"], batch_size=1000)
                self.stdout.write(f"Updated readings: {len(readings_to_update)}")
            else:
                self.stdout.write("No reading updated.")
        else:
            self.stdout.write("Dry run only. Use --apply to persist changes.")
