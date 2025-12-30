import json
from datetime import date
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from core.models import Entity
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter import ElecMeter
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from transactions.models.year_config import YearConfig

ENR_RATIO = 0.25


class GenerateMeterReadingsReportCommandTest(TestCase):
    def setUp(self):
        self.cpo = Entity.objects.create(name="CPO", entity_type=Entity.CPO, has_elec=True)

        self.charge_point_application_a = ElecChargePointApplication.objects.create(
            status=ElecChargePointApplication.ACCEPTED,
            cpo=self.cpo,
        )

        YearConfig.objects.create(year=2022, renewable_share=ENR_RATIO * 100)
        YearConfig.objects.create(year=2023, renewable_share=ENR_RATIO * 100)

    def create_meter_reading_application(self, cpo, quarter=1, year=2023):
        return ElecMeterReadingApplication.objects.create(
            status=ElecMeterReadingApplication.ACCEPTED,
            quarter=quarter,
            year=year,
            cpo=cpo,
        )

    def create_charge_point_with_meter(
        self,
        *,
        cpo,
        application,
        cp_suffix,
        initial_index,
        initial_index_date,
    ):
        charge_point = ElecChargePoint.objects.create(
            application=application,
            cpo=cpo,
            charge_point_id=f"{cpo.name}-CP-{cp_suffix}",
            current_type=ElecChargePoint.AC,
            installation_date=initial_index_date,
            is_article_2=False,
            measure_reference_point_id=f"MRP-{cp_suffix}",
            station_name=f"{cpo.name} Station {cp_suffix}",
            station_id=f"STAT-{cpo.id}-{cp_suffix}",
            nominal_power=50,
        )
        meter = ElecMeter.objects.create(
            mid_certificate=f"MID-{cpo.id}-{cp_suffix}",
            initial_index=initial_index,
            initial_index_date=initial_index_date,
            charge_point=charge_point,
        )
        charge_point.current_meter = meter
        charge_point.save(update_fields=["current_meter"])
        return charge_point, meter

    def create_new_meter_for_charge_point(
        self,
        *,
        charge_point,
        meter_suffix,
        initial_index,
        initial_index_date,
    ):
        meter = ElecMeter.objects.create(
            mid_certificate=f"{charge_point.charge_point_id}-{meter_suffix}",
            initial_index=initial_index,
            initial_index_date=initial_index_date,
            charge_point=charge_point,
        )
        charge_point.current_meter = meter
        charge_point.save(update_fields=["current_meter"])
        return meter

    def create_meter_reading(
        self,
        *,
        cpo,
        application,
        meter,
        extracted_energy,
        energy_used_since_last_reading,
        reading_date,
        renewable_energy=None,
    ):
        return ElecMeterReading.objects.create(
            extracted_energy=extracted_energy,
            reading_date=reading_date,
            cpo=cpo,
            application=application,
            meter=meter,
            energy_used_since_last_reading=energy_used_since_last_reading,
            renewable_energy=renewable_energy or energy_used_since_last_reading * ENR_RATIO,
            days_since_last_reading=30,
        )

    def run_command(self, year=None):
        report = call_command("generate_meter_readings_report", year=year, stdout=StringIO())
        return json.loads(report)

    def test_report_returns_zero_delta_when_values_are_correct(self):
        _, meter = self.create_charge_point_with_meter(
            cpo=self.cpo,
            application=self.charge_point_application_a,
            cp_suffix="001",
            initial_index=100,
            initial_index_date=date(2023, 1, 1),
        )

        # Q1
        app_q1 = self.create_meter_reading_application(
            self.cpo,
            quarter=1,
            year=2023,
        )
        self.create_meter_reading(
            cpo=self.cpo,
            application=app_q1,
            meter=meter,
            extracted_energy=150,
            energy_used_since_last_reading=50,
            reading_date=date(2023, 3, 1),  # end of Q1
        )

        # Q2
        app_q2 = self.create_meter_reading_application(
            self.cpo,
            quarter=2,
            year=2023,
        )
        self.create_meter_reading(
            cpo=self.cpo,
            application=app_q2,
            meter=meter,
            extracted_energy=210,
            energy_used_since_last_reading=60,
            reading_date=date(2023, 7, 1),  # end of Q2
        )

        self.assertEqual(self.run_command(year=2023), {})

    def test_report_accumulates_positive_and_negative_deltas(self):
        _, meter = self.create_charge_point_with_meter(
            cpo=self.cpo,
            application=self.charge_point_application_a,
            cp_suffix="002",
            initial_index=200,
            initial_index_date=date(2023, 1, 1),
        )

        # Q1
        app_q1 = self.create_meter_reading_application(
            self.cpo,
            quarter=1,
            year=2023,
        )
        self.create_meter_reading(
            cpo=self.cpo,
            application=app_q1,
            meter=meter,
            extracted_energy=250,  # should be 50 (250 - 200)
            energy_used_since_last_reading=90,
            reading_date=date(2023, 3, 1),  # end of Q1
        )

        # Q2
        app_q2 = self.create_meter_reading_application(
            self.cpo,
            quarter=2,
            year=2023,
        )
        self.create_meter_reading(
            cpo=self.cpo,
            application=app_q2,
            meter=meter,
            extracted_energy=290,
            energy_used_since_last_reading=35,  # should be 40 (290 - 250)
            reading_date=date(2023, 7, 1),  # end of Q2
        )

        self.assertEqual(
            self.run_command(year=2023),
            {"CPO": 35.0 * ENR_RATIO},
        )

    def test_report_handles_meter_change_between_applications(self):
        charge_point, meter_1 = self.create_charge_point_with_meter(
            cpo=self.cpo,
            application=self.charge_point_application_a,
            cp_suffix="003",
            initial_index=300,
            initial_index_date=date(2023, 1, 1),
        )

        # Q1
        app_q1 = self.create_meter_reading_application(
            self.cpo,
            quarter=1,
            year=2023,
        )
        self.create_meter_reading(
            cpo=self.cpo,
            application=app_q1,
            meter=meter_1,
            extracted_energy=360,
            energy_used_since_last_reading=60,  # correct
            reading_date=date(2023, 3, 1),  # end of Q1
        )

        # Q2, change meter, but save correct deltas
        app_q2 = self.create_meter_reading_application(
            self.cpo,
            quarter=2,
            year=2023,
        )
        meter_2 = self.create_new_meter_for_charge_point(
            charge_point=charge_point,
            meter_suffix="replacement-1",
            initial_index=1000,
            initial_index_date=date(2023, 6, 1),  # during Q2
        )
        self.create_meter_reading(
            cpo=self.cpo,
            application=app_q2,
            meter=meter_2,
            extracted_energy=1050,
            energy_used_since_last_reading=50,  # correct
            reading_date=date(2023, 7, 1),  # end of Q2
        )

        # Q3, change meter, but save incorrect delta
        app_q3 = self.create_meter_reading_application(
            self.cpo,
            quarter=3,
            year=2023,
        )
        meter_3 = self.create_new_meter_for_charge_point(
            charge_point=charge_point,
            meter_suffix="replacement-2",
            initial_index=10,
            initial_index_date=date(2023, 9, 1),  # during Q3
        )
        self.create_meter_reading(
            cpo=self.cpo,
            application=app_q3,
            meter=meter_3,
            extracted_energy=100,
            energy_used_since_last_reading=150,  # should be 90
            reading_date=date(2023, 10, 1),  # end of Q3
        )

        self.assertEqual(
            self.run_command(year=2023),
            {"CPO": (150 - 90) * ENR_RATIO},
        )

    def test_report_uses_renewable_energy_when_missing_energy_delta(self):
        app_q1 = self.create_meter_reading_application(
            self.cpo,
            quarter=1,
            year=2023,
        )
        _, meter = self.create_charge_point_with_meter(
            cpo=self.cpo,
            application=self.charge_point_application_a,
            cp_suffix="004",
            initial_index=100,
            initial_index_date=date(2023, 1, 1),
        )
        self.create_meter_reading(
            cpo=self.cpo,
            application=app_q1,
            meter=meter,
            extracted_energy=150,
            energy_used_since_last_reading=0,  # we didn't compute energy_used_since_last_reading
            renewable_energy=10,  # but we did compute renewable energy, so we use it to guess energy_used_since_last_reading
            reading_date=date(2023, 3, 1),
        )

        self.assertEqual(
            self.run_command(year=2023),
            {"CPO": -2.5},
        )

    def test_report_without_year_filter_includes_multiple_years(self):
        _, meter = self.create_charge_point_with_meter(
            cpo=self.cpo,
            application=self.charge_point_application_a,
            cp_suffix="005",
            initial_index=100,
            initial_index_date=date(2022, 1, 1),
        )

        app_2022_q4 = self.create_meter_reading_application(
            self.cpo,
            quarter=4,
            year=2022,
        )
        self.create_meter_reading(
            cpo=self.cpo,
            application=app_2022_q4,
            meter=meter,
            extracted_energy=150,
            energy_used_since_last_reading=40,  # should be 50 => -10 delta
            reading_date=date(2022, 12, 31),
        )

        app_2023_q1 = self.create_meter_reading_application(
            self.cpo,
            quarter=1,
            year=2023,
        )
        self.create_meter_reading(
            cpo=self.cpo,
            application=app_2023_q1,
            meter=meter,
            extracted_energy=230,
            energy_used_since_last_reading=100,  # should be 80 => +20 delta
            reading_date=date(2023, 3, 31),
        )

        self.assertEqual(
            self.run_command(),
            {"CPO": 2.5},
        )

        self.assertEqual(
            self.run_command(year=2023),
            {"CPO": 5.0},
        )
