import json
from datetime import date
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from core.models import Entity
from elec.models.elec_certificate_readjustment import ElecCertificateReadjustment
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter import ElecMeter
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.models.elec_provision_certificate import ElecProvisionCertificate
from transactions.models.year_config import YearConfig

ENR_RATIO = 0.25


class GenerateMeterReadingsReportCommandTest(TestCase):
    def setUp(self):
        self.cpo = Entity.objects.create(name="CPO", entity_type=Entity.CPO, has_elec=True)

        self.charge_point_application = ElecChargePointApplication.objects.create(
            status=ElecChargePointApplication.ACCEPTED,
            cpo=self.cpo,
        )

        self.charge_point = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id=f"{self.cpo.name}-CP-001",
            current_type=ElecChargePoint.AC,
            installation_date=date(2023, 1, 1),
            is_article_2=False,
            measure_reference_point_id="MRP-001",
            station_name=f"{self.cpo.name} Station 001",
            station_id=f"STAT-{self.cpo.id}-001",
            nominal_power=50,
        )
        self.meter = ElecMeter.objects.create(
            mid_certificate=f"MID-{self.cpo.id}-001",
            initial_index=1000,
            initial_index_date=date(2023, 1, 1),
            charge_point=self.charge_point,
        )
        self.charge_point.current_meter = self.meter
        self.charge_point.save(update_fields=["current_meter"])

        YearConfig.objects.create(year=2022, renewable_share=ENR_RATIO * 100)
        YearConfig.objects.create(year=2023, renewable_share=ENR_RATIO * 100)

    def setup_meter_reading(self, quarter, year, reading_energy, reading_date, certificate_energy, meter=None):
        application = ElecMeterReadingApplication.objects.create(
            status=ElecMeterReadingApplication.ACCEPTED,
            quarter=quarter,
            year=year,
            cpo=self.cpo,
        )

        meter_reading = ElecMeterReading.objects.create(
            extracted_energy=reading_energy,
            reading_date=reading_date,
            cpo=self.cpo,
            application=application,
            meter=meter or self.meter,
            enr_ratio=ENR_RATIO,
        )

        ElecProvisionCertificate.objects.create(
            cpo=self.cpo,
            quarter=1,
            year=2024,
            operating_unit="FRBLA",
            source=ElecProvisionCertificate.METER_READINGS,
            energy_amount=certificate_energy,
            remaining_energy_amount=certificate_energy,
        )

        return meter_reading

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

    def run_command(self, year=None, apply_readjustments=False):
        report = call_command("generate_meter_readings_report", year=year, apply=apply_readjustments, stdout=StringIO())
        return json.loads(report)

    def test_report_returns_zero_delta_when_values_are_correct(self):
        # Q1
        self.setup_meter_reading(
            quarter=1,
            year=2023,
            reading_energy=1500,
            reading_date=date(2023, 3, 1),
            certificate_energy=(1500 - 1000) * ENR_RATIO / 1000,
        )

        # Q2
        self.setup_meter_reading(
            quarter=2,
            year=2023,
            reading_energy=2100,
            reading_date=date(2023, 7, 1),
            certificate_energy=(2100 - 1500) * ENR_RATIO / 1000,
        )

        self.assertEqual(self.run_command(), {})

    def test_report_handles_meter_change_between_applications(self):
        # Q1
        self.setup_meter_reading(
            quarter=1,
            year=2023,
            reading_energy=1600,
            reading_date=date(2023, 3, 1),
            certificate_energy=600 * ENR_RATIO / 1000,
        )

        # Q2, change meter, but save correct deltas
        meter_2 = self.create_new_meter_for_charge_point(
            charge_point=self.charge_point,
            meter_suffix="replacement-1",
            initial_index=2000,
            initial_index_date=date(2023, 6, 1),
        )
        self.setup_meter_reading(
            meter=meter_2,
            quarter=2,
            year=2023,
            reading_energy=2500,
            reading_date=date(2023, 7, 1),
            certificate_energy=500 * ENR_RATIO / 1000,
        )

        # Q3, change meter, but save incorrect delta
        meter_3 = self.create_new_meter_for_charge_point(
            charge_point=self.charge_point,
            meter_suffix="replacement-1",
            initial_index=100,
            initial_index_date=date(2023, 9, 1),
        )
        self.setup_meter_reading(
            meter=meter_3,
            quarter=3,
            year=2023,
            reading_energy=1000,
            reading_date=date(2023, 10, 1),
            certificate_energy=1500 * ENR_RATIO / 1000,
        )

        expected_readjustment_energy = (1500 - 900) * ENR_RATIO

        self.assertEqual(
            self.run_command(apply_readjustments=True),
            {"CPO": expected_readjustment_energy},
        )
        # Check that readjustments where created in database
        readjustment = ElecCertificateReadjustment.objects.filter(
            cpo=self.cpo, error_source=ElecCertificateReadjustment.METER_READINGS
        ).get()

        self.assertEqual(readjustment.energy_amount, expected_readjustment_energy / 1000)

    def test_report_takes_already_defined_readjustments_into_account(self):
        self.setup_meter_reading(
            quarter=1,
            year=2023,
            reading_energy=1500,
            reading_date=date(2023, 3, 1),
            certificate_energy=900 * ENR_RATIO / 1000,  # should be 500 (1500 - 1000)
        )

        self.assertEqual(
            self.run_command(apply_readjustments=True),
            {"CPO": 400 * ENR_RATIO},
        )

        self.assertEqual(
            self.run_command(),
            {},
        )

    def test_report_takes_admin_error_readjustments_into_account(self):
        self.setup_meter_reading(
            quarter=1,
            year=2023,
            reading_energy=15000,
            reading_date=date(2023, 3, 1),
            certificate_energy=4000 * ENR_RATIO / 1000,  # should be 14000 (15000 - 1000)
        )

        self.assertEqual(
            self.run_command(),
            {"CPO": -10000 * ENR_RATIO},
        )

        ElecProvisionCertificate.objects.create(
            cpo=self.cpo,
            quarter=1,
            year=2023,
            energy_amount=10000 * ENR_RATIO / 1000,
            remaining_energy_amount=10000 * ENR_RATIO / 1000,
            source=ElecProvisionCertificate.ADMIN_ERROR_COMPENSATION,
        )

        self.assertEqual(
            self.run_command(),
            {},
        )
