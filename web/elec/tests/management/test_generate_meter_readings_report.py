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

        self.charge_point_application_a = ElecChargePointApplication.objects.create(
            status=ElecChargePointApplication.ACCEPTED,
            cpo=self.cpo,
        )

        YearConfig.objects.create(year=2022, renewable_share=ENR_RATIO * 100)
        YearConfig.objects.create(year=2023, renewable_share=ENR_RATIO * 100)

    def create_provision_certificate(self, cpo, amount, source=ElecProvisionCertificate.METER_READINGS):
        return ElecProvisionCertificate.objects.create(
            cpo=cpo,
            quarter=1,
            year=2024,
            operating_unit="FRBLA",
            source=source,
            energy_amount=amount,
            remaining_energy_amount=amount,
        )

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
        reading_date,
    ):
        return ElecMeterReading.objects.create(
            extracted_energy=extracted_energy,
            reading_date=reading_date,
            cpo=cpo,
            application=application,
            meter=meter,
            enr_ratio=ENR_RATIO,
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
            reading_date=date(2023, 3, 1),  # end of Q1
        )
        self.create_provision_certificate(cpo=self.cpo, amount=(150 - 100) * ENR_RATIO / 1000)

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
            reading_date=date(2023, 7, 1),  # end of Q2
        )
        self.create_provision_certificate(cpo=self.cpo, amount=(210 - 150) * ENR_RATIO / 1000)

        self.assertEqual(self.run_command(), {})

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
            reading_date=date(2023, 3, 1),  # end of Q1
        )
        self.create_provision_certificate(
            cpo=self.cpo,
            amount=60 * ENR_RATIO / 1000,  # correct
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
            reading_date=date(2023, 7, 1),  # end of Q2
        )
        self.create_provision_certificate(
            cpo=self.cpo,
            amount=50 * ENR_RATIO / 1000,  # correct
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
            reading_date=date(2023, 10, 1),  # end of Q3
        )
        self.create_provision_certificate(
            cpo=self.cpo,
            amount=150 * ENR_RATIO / 1000,  # should be 90
        )

        self.assertEqual(
            self.run_command(),
            {"CPO": (150 - 90) * ENR_RATIO},
        )

    def test_report_takes_already_defined_readjustments_into_account(self):
        _, meter = self.create_charge_point_with_meter(
            cpo=self.cpo,
            application=self.charge_point_application_a,
            cp_suffix="002",
            initial_index=200,
            initial_index_date=date(2023, 1, 1),
        )

        app_q1 = self.create_meter_reading_application(
            self.cpo,
            quarter=1,
            year=2023,
        )
        self.create_meter_reading(
            cpo=self.cpo,
            application=app_q1,
            meter=meter,
            extracted_energy=250,
            reading_date=date(2023, 3, 1),  # end of Q1
        )
        self.create_provision_certificate(
            cpo=self.cpo,
            amount=90 * ENR_RATIO / 1000,  # should be 50 (250 - 200)
        )

        self.assertEqual(
            self.run_command(),
            {"CPO": 40 * ENR_RATIO},
        )

        ElecCertificateReadjustment.objects.create(
            cpo=self.cpo, energy_amount=40 * ENR_RATIO / 1000, error_source=ElecCertificateReadjustment.METER_READINGS
        )
        ElecCertificateReadjustment.objects.create(
            cpo=self.cpo,
            energy_amount=1000,
            error_source=ElecCertificateReadjustment.QUALICHARGE,  # this should be ignored
        )

        self.assertEqual(
            self.run_command(),
            {},
        )

    def test_report_takes_admin_error_readjustments_into_account(self):
        _, meter = self.create_charge_point_with_meter(
            cpo=self.cpo,
            application=self.charge_point_application_a,
            cp_suffix="002",
            initial_index=200,
            initial_index_date=date(2023, 1, 1),
        )

        app_q1 = self.create_meter_reading_application(
            self.cpo,
            quarter=1,
            year=2023,
        )
        self.create_meter_reading(
            cpo=self.cpo,
            application=app_q1,
            meter=meter,
            extracted_energy=250,
            reading_date=date(2023, 3, 1),  # end of Q1
        )
        self.create_provision_certificate(
            cpo=self.cpo,
            amount=40 * ENR_RATIO / 1000,  # should be 50 (250 - 200)
        )

        self.assertEqual(
            self.run_command(),
            {"CPO": -10 * ENR_RATIO},
        )

        self.create_provision_certificate(
            cpo=self.cpo, amount=10 * ENR_RATIO / 1000, source=ElecProvisionCertificate.ADMIN_ERROR_COMPENSATION
        )

        self.assertEqual(
            self.run_command(),
            {},
        )
