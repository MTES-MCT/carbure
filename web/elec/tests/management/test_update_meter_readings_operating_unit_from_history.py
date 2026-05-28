from datetime import date, datetime, time
from io import StringIO
from uuid import uuid4

from django.apps import apps
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from core.models import Entity
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter import ElecMeter
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication


class UpdateMeterReadingsOperatingUnitFromHistoryTest(TestCase):
    def setUp(self):
        suffix = uuid4().hex[:8]
        self.cpo = Entity.objects.create(name=f"CPO-{suffix}", entity_type=Entity.CPO, has_elec=True)
        self.charge_point_application = ElecChargePointApplication.objects.create(
            status=ElecChargePointApplication.ACCEPTED,
            cpo=self.cpo,
        )
        self.meter_reading_application = ElecMeterReadingApplication.objects.create(
            status=ElecMeterReadingApplication.ACCEPTED,
            quarter=2,
            year=2024,
            cpo=self.cpo,
        )

    def _create_reading(self, *, charge_point_id, reading_date, operating_unit, application=None):
        charge_point = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id=charge_point_id,
            current_type=ElecChargePoint.AC,
            installation_date=date(2023, 1, 1),
            is_article_2=False,
            measure_reference_point_id=f"MRP-{uuid4().hex[:6]}",
            station_name=f"Station-{uuid4().hex[:6]}",
            station_id=f"STAT-{uuid4().hex[:6]}",
            nominal_power=22,
        )
        meter = ElecMeter.objects.create(
            mid_certificate=f"MID-{uuid4().hex[:8]}",
            initial_index=1000,
            initial_index_date=date(2023, 1, 1),
            charge_point=charge_point,
        )
        charge_point.current_meter = meter
        charge_point.save(update_fields=["current_meter"])

        reading = ElecMeterReading.objects.create(
            extracted_energy=1200,
            reading_date=reading_date,
            cpo=self.cpo,
            application=application or self.meter_reading_application,
            meter=meter,
            enr_ratio=0.25,
            operating_unit=operating_unit,
        )
        return reading, charge_point

    def _set_charge_point_history(self, charge_point, timeline):
        # Build history rows by mutating charge_point_id, then force deterministic history_date values.
        for _, charge_point_id in timeline[1:]:
            charge_point.charge_point_id = charge_point_id
            charge_point.save(update_fields=["charge_point_id"])

        history_model = apps.get_model("elec", "ElecChargePointHistory")
        history_rows = list(history_model.objects.filter(id=charge_point.id).order_by("history_id"))
        self.assertGreaterEqual(len(history_rows), len(timeline))
        history_rows = history_rows[-len(timeline) :]

        for history_row, (history_day, charge_point_id) in zip(history_rows, timeline):
            history_row.charge_point_id = charge_point_id
            history_row.history_date = timezone.make_aware(datetime.combine(history_day, time(12, 0)))
            history_row.save(update_fields=["charge_point_id", "history_date"])

    def _run_command(self, *, apply=False, year=None, cpo_id=None):
        stdout = StringIO()
        kwargs = {"stdout": stdout, "apply": apply}
        if year is not None:
            kwargs["year"] = year
        if cpo_id is not None:
            kwargs["cpo"] = cpo_id
        call_command("update_meter_readings_operating_unit_from_history", **kwargs)
        return stdout.getvalue()

    def test_apply_updates_reading_using_latest_history_before_reading_date(self):
        reading, charge_point = self._create_reading(
            charge_point_id="AAAAA-initial",
            reading_date=date(2024, 6, 15),
            operating_unit="ZZZZZ",
        )
        self._set_charge_point_history(
            charge_point,
            [
                (date(2024, 1, 1), "AAAAA-initial"),
                (date(2024, 5, 1), "BBBBB-middle"),
                (date(2024, 7, 1), "CCCCC-later"),
            ],
        )

        output = self._run_command(apply=True)

        reading.refresh_from_db()
        self.assertEqual(reading.operating_unit, "BBBBB")
        self.assertIn("Mismatches found: 1", output)
        self.assertIn("Updated readings: 1", output)

    def test_no_update_when_no_history_exists_before_reading_date(self):
        reading, charge_point = self._create_reading(
            charge_point_id="AAAAA-initial",
            reading_date=date(2024, 3, 10),
            operating_unit="ZZZZZ",
        )
        self._set_charge_point_history(
            charge_point,
            [
                (date(2024, 4, 1), "AAAAA-initial"),
                (date(2024, 6, 1), "BBBBB-middle"),
            ],
        )

        output = self._run_command(apply=True)

        reading.refresh_from_db()
        self.assertEqual(reading.operating_unit, "ZZZZZ")
        self.assertIn("No operating_unit mismatch found.", output)
        self.assertIn("Mismatches found: 0", output)
        self.assertIn("No reading updated.", output)

    def test_no_update_when_operating_unit_already_matches_expected(self):
        reading, charge_point = self._create_reading(
            charge_point_id="AAAAA-initial",
            reading_date=date(2024, 6, 15),
            operating_unit="BBBBB",
        )
        self._set_charge_point_history(
            charge_point,
            [
                (date(2024, 1, 1), "AAAAA-initial"),
                (date(2024, 5, 1), "BBBBB-middle"),
            ],
        )

        output = self._run_command(apply=True)

        reading.refresh_from_db()
        self.assertEqual(reading.operating_unit, "BBBBB")
        self.assertIn("No operating_unit mismatch found.", output)
        self.assertIn("Mismatches found: 0", output)
