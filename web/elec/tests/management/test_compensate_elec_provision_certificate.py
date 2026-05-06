import json
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from core.models import Entity
from core.tests_utils import assert_object_contains_data
from elec.management.commands import compensate_elec_provision_certificate as command_module
from elec.models import ElecProvisionCertificate
from elec.tests.utils import setup_cpo_with_meter_readings
from entity.factories.entity import EntityFactory

COMPENSATION_YEAR = 2025


def run_command(enr_ratio, apply=False, log=False, year=COMPENSATION_YEAR):
    report = call_command(
        "compensate_elec_provision_certificate",
        enr_ratio=enr_ratio,
        year=year,
        apply=apply,
        log=log,
        stdout=StringIO(),
    )
    return json.loads(report)


class CompensateElecProvisionCertificateCommandTest(TestCase):
    def setUp(self):
        self.cpo1 = EntityFactory.create(entity_type=Entity.CPO)
        self.last_year = COMPENSATION_YEAR

    def create_certificate(
        self,
        *,
        source,
        energy_amount,
        enr_ratio=0.25,
        quarter=1,
        year=None,
        operating_unit="00001",
    ):
        return ElecProvisionCertificate.objects.create(
            cpo=self.cpo1,
            quarter=quarter,
            year=year or self.last_year,
            operating_unit=operating_unit,
            source=source,
            energy_amount=energy_amount,
            enr_ratio=enr_ratio,
        )

    def test_returns_empty_list_when_no_eligible_certificates(self):
        result = run_command(enr_ratio=30)

        self.assertEqual(result, [])

    def test_returns_certificates_when_delta_positive_from_provision_certificates(self):
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=1.0, enr_ratio=0.25)
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=2, energy_amount=1.5, enr_ratio=0.25)

        result = run_command(enr_ratio=30)

        # One compensation certificate per quarter when delta is positive.
        self.assertEqual(len(result), 2)

        # Energy amount in certificate is already renewable energy.
        # So we first recompute total energy with old ratio, then re-apply new ratio:
        # quarter 1: (1.0 / 0.25) * 0.30 - 1.0 = 0.20 MWh
        # quarter 2: (1.5 / 0.25) * 0.30 - 1.5 = 0.30 MWh
        expected_data = [
            {
                "cpo_id": self.cpo1.id,
                "quarter": 1,
                "year": 2025,
                "operating_unit": "00001",
                "energy_amount": 0.2,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
            {
                "cpo_id": self.cpo1.id,
                "quarter": 2,
                "year": 2025,
                "operating_unit": "00001",
                "energy_amount": 0.3,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
        ]
        for i, cert in enumerate(result):
            assert_object_contains_data(
                self,
                cert,
                expected_data[i],
            )

    def test_returns_no_certificate_when_delta_zero(self):
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=2.0, enr_ratio=0.25)
        self.create_certificate(source=ElecProvisionCertificate.QUALICHARGE, quarter=2, energy_amount=3.0, enr_ratio=0.25)

        result = run_command(enr_ratio=25)

        self.assertEqual(result, [])

    def test_excludes_compensation_sources_from_base_calculation(self):
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=1.0, enr_ratio=0.25)
        self.create_certificate(
            source=ElecProvisionCertificate.ADMIN_ERROR_COMPENSATION,
            quarter=1,
            energy_amount=10.0,
            enr_ratio=0.25,
        )

        result = run_command(enr_ratio=30)

        # Only MANUAL contributes to base computation: expected delta = 1.0 * (0.30 / 0.25 - 1) = 0.2
        self.assertEqual(len(result), 1)
        assert_object_contains_data(
            self,
            result[0],
            {
                "cpo_id": self.cpo1.id,
                "quarter": 1,
                "year": 2025,
                "operating_unit": "00001",
                "energy_amount": 0.2,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
        )

    def test_excludes_meter_readings_source_from_base_calculation(self):
        self.create_certificate(source=ElecProvisionCertificate.METER_READINGS, quarter=1, energy_amount=1.0, enr_ratio=0.25)

        result = run_command(enr_ratio=30)

        self.assertEqual(result, [])

    def test_returns_no_certificate_when_certificate_already_created(self):
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=1.0, enr_ratio=0.25)

        # Create compensation certificate for this key
        result = run_command(enr_ratio=30, apply=True)

        self.assertEqual(len(result), 1)

        # Should return no certificates because compensation is already created for this key.
        new_result = run_command(enr_ratio=35, apply=True)

        self.assertEqual(new_result, [])

    def test_returns_certificates_for_quarterly_meter_readings(self):
        setup_cpo_with_meter_readings(self.cpo1, charge_points_count=1, years=[2025], quarters=[1, 2])

        result = run_command(enr_ratio=30)

        self.assertEqual(len(result), 2)
        expected_data = [
            {
                "cpo_id": self.cpo1.id,
                "quarter": 1,
                "year": 2025,
                "operating_unit": "00001",
                "energy_amount": 0.01,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
            {
                "cpo_id": self.cpo1.id,
                "quarter": 2,
                "year": 2025,
                "operating_unit": "00001",
                "energy_amount": 0.01,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
        ]
        for i, cert in enumerate(result):
            assert_object_contains_data(self, cert, expected_data[i])

    def test_returns_no_certificate_for_meter_readings_when_delta_negative(self):
        setup_cpo_with_meter_readings(self.cpo1, charge_points_count=1, years=[2025], quarters=[1, 2])

        result = run_command(enr_ratio=20)

        self.assertEqual(result, [])

    def test_returns_no_certificate_for_meter_readings_when_compensation_already_exists(self):
        setup_cpo_with_meter_readings(self.cpo1, charge_points_count=1, years=[2025], quarters=[1])
        ElecProvisionCertificate.objects.create(
            cpo=self.cpo1,
            quarter=1,
            year=2025,
            operating_unit="00001",
            source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            energy_amount=0.01,
            enr_ratio=0.30,
        )

        result = run_command(enr_ratio=30)

        self.assertEqual(result, [])


class CompensateElecProvisionCertificateHelpersTest(TestCase):
    def setUp(self):
        self.cpo = EntityFactory.create(entity_type=Entity.CPO, name="CPO Test")

    def test_build_certificate_key(self):
        key = command_module._build_certificate_key(self.cpo.id, 1, COMPENSATION_YEAR, "00001")
        self.assertEqual(key, f"{self.cpo.id}-1-{COMPENSATION_YEAR}-00001")

    def test_get_existing_compensation_keys_only_returns_compensation_source(self):
        ElecProvisionCertificate.objects.create(
            cpo=self.cpo,
            quarter=1,
            year=COMPENSATION_YEAR,
            operating_unit="00001",
            source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            energy_amount=1.0,
            enr_ratio=0.30,
        )
        ElecProvisionCertificate.objects.create(
            cpo=self.cpo,
            quarter=2,
            year=COMPENSATION_YEAR,
            operating_unit="00001",
            source=ElecProvisionCertificate.MANUAL,
            energy_amount=2.0,
            enr_ratio=0.25,
        )

        keys = command_module._get_existing_compensation_keys(COMPENSATION_YEAR)

        self.assertEqual(keys, {f"{self.cpo.id}-1-{COMPENSATION_YEAR}-00001"})
