import json
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from core.models import Entity
from core.tests_utils import assert_object_contains_data
from elec.models import ElecProvisionCertificate
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

    def test_excludes_enr_ratio_compensation_source_from_base_calculation(self):
        self.create_certificate(
            source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            quarter=1,
            energy_amount=1.0,
            enr_ratio=0.25,
        )

        result = run_command(enr_ratio=30)

        self.assertEqual(result, [])

    def test_includes_meter_readings_source_in_base_calculation(self):
        self.create_certificate(source=ElecProvisionCertificate.METER_READINGS, quarter=1, energy_amount=1.0, enr_ratio=0.25)

        result = run_command(enr_ratio=30)

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

    def test_returns_no_certificate_when_certificate_already_created(self):
        self.create_certificate(source=ElecProvisionCertificate.MANUAL, quarter=1, energy_amount=1.0, enr_ratio=0.25)

        # Create compensation certificate for this key
        result = run_command(enr_ratio=30, apply=True)

        self.assertEqual(len(result), 1)

        # Should return no certificates because compensation is already created for this key.
        new_result = run_command(enr_ratio=35, apply=True)

        self.assertEqual(new_result, [])
