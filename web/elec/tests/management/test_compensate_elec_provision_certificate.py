from datetime import date
from unittest.mock import patch

from django.test import TestCase

from core.models import Entity
from core.tests_utils import assert_object_contains_data
from elec.management.scripts.compensate_elec_provision_certificate import (
    compensate_elec_provision_certificate,
)
from elec.models import ElecProvisionCertificate
from elec.tests.utils import setup_cpo_with_meter_readings
from entity.factories.entity import EntityFactory

# Date fixe pour que last_year soit 2023 dans tous les tests
FIXED_TODAY = date(2026, 2, 15)


class CompensateElecProvisionCertificateCommandTest(TestCase):
    def setUp(self):
        self.cpo1 = EntityFactory.create(entity_type=Entity.CPO)

    @patch("elec.management.scripts.compensate_elec_provision_certificate.date")
    def test_returns_empty_list_when_no_meter_readings(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY

        result = compensate_elec_provision_certificate(30)

        self.assertEqual(result, [])

    @patch("elec.management.scripts.compensate_elec_provision_certificate.date")
    def test_returns_certificates_when_delta_positive(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        setup_cpo_with_meter_readings(self.cpo1, charge_points_count=1, quarters=[1, 2])

        result = compensate_elec_provision_certificate(30)

        # It should return 2 certificates, data contains 1 meter reading application for
        # each quarter of the year * 1 meter reading per application (2 quarters * 1 meter reading = 2)
        self.assertEqual(len(result), 2)

        # The energy amount before compensation is 25 kWh, the energy amount
        # after compensation is 30 kWh, so the delta is 5 kWh
        expected_data = [
            {
                "cpo_id": self.cpo1.id,
                "quarter": 1,
                "year": 2025,
                "operating_unit": "00001",
                "energy_amount": 5,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
            {
                "cpo_id": self.cpo1.id,
                "quarter": 2,
                "year": 2025,
                "operating_unit": "00001",
                "energy_amount": 5,
                "source": ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
            },
        ]
        for i, cert in enumerate(result):
            assert_object_contains_data(
                self,
                cert,
                expected_data[i],
            )

    @patch("elec.management.scripts.compensate_elec_provision_certificate.date")
    def test_returns_no_certificate_when_delta_zero(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        setup_cpo_with_meter_readings(self.cpo1, charge_points_count=1, quarters=[1, 2])

        result = compensate_elec_provision_certificate(25)

        # It should return an empty list because the enr ratio is the same as the energy
        # amount before compensation, so the delta is 0
        self.assertEqual(result, [])

    @patch("elec.management.scripts.compensate_elec_provision_certificate.date")
    def test_returns_no_certificate_when_certificate_already_created(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        setup_cpo_with_meter_readings(self.cpo1, charge_points_count=1, quarters=[1, 2])

        # Create certificates
        result = compensate_elec_provision_certificate(30, apply=True)

        self.assertEqual(len(result), 2)

        # Should return no certificates because the certificates are already created
        new_result = compensate_elec_provision_certificate(35, apply=True)

        self.assertEqual(new_result, [])
