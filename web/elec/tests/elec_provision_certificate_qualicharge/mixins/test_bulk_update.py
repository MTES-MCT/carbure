from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from elec.factories import ElecProvisionCertificateQualichargeFactory
from elec.models import ElecProvisionCertificate, ElecProvisionCertificateQualicharge
from entity.factories import EntityFactory


class BulkUpdateMixinTest(TestCase):
    """Integration tests for the bulk update mixin - focuses on validation state transitions"""

    def setUp(self):
        self.cpo = EntityFactory.create(
            name="Test CPO",
            entity_type=Entity.CPO,
            has_elec=True,
            registration_id="123456789",
        )

        self.cert1 = ElecProvisionCertificateQualichargeFactory.create(
            cpo=self.cpo,
            operating_unit="FR001",
            station_id="FRXYZP111111",
            energy_amount=1000.0,
            validated_by=ElecProvisionCertificateQualicharge.NO_ONE,
        )

        self.cert2 = ElecProvisionCertificateQualichargeFactory.create(
            cpo=self.cpo,
            operating_unit="FR001",
            station_id="FRXYZP222222",
            energy_amount=2000.0,
            validated_by=ElecProvisionCertificateQualicharge.NO_ONE,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.cpo, "RW")],
        )

        # Base data for tests
        self.data = {
            "certificate_ids": [self.cert1.id, self.cert2.id],
            "validated_by": ElecProvisionCertificateQualicharge.CPO,
        }

        self.post_params = {
            "path": reverse("elec-provision-certificate-qualicharge-bulk-update"),
            "query_params": {"entity_id": self.cpo.id},
            "content_type": "application/json",
        }

    def test_bulk_update_no_one_to_cpo(self):
        """Test updating from NO_ONE to CPO"""
        response = self.client.post(
            **self.post_params,
            data=self.data,
        )

        self.assertEqual(response.status_code, 200)

        self.cert1.refresh_from_db()
        self.cert2.refresh_from_db()
        self.assertEqual(self.cert1.validated_by, ElecProvisionCertificateQualicharge.CPO)
        self.assertEqual(self.cert2.validated_by, ElecProvisionCertificateQualicharge.CPO)

        # No provision certificate should be created
        self.assertEqual(ElecProvisionCertificate.objects.count(), 0)

    def test_bulk_update_no_one_to_dgec(self):
        """Test updating from NO_ONE to DGEC"""
        self.data["validated_by"] = ElecProvisionCertificateQualicharge.DGEC

        response = self.client.post(
            **self.post_params,
            data=self.data,
        )

        self.assertEqual(response.status_code, 200)

        self.cert1.refresh_from_db()
        self.cert2.refresh_from_db()
        self.assertEqual(self.cert1.validated_by, ElecProvisionCertificateQualicharge.DGEC)
        self.assertEqual(self.cert2.validated_by, ElecProvisionCertificateQualicharge.DGEC)

    def test_bulk_update_cpo_to_both(self):
        """Test updating from CPO to BOTH (DGEC validation)"""
        self.cert1.validated_by = ElecProvisionCertificateQualicharge.CPO
        self.cert1.save()
        self.cert2.validated_by = ElecProvisionCertificateQualicharge.CPO
        self.cert2.save()

        self.data["validated_by"] = ElecProvisionCertificateQualicharge.DGEC

        response = self.client.post(
            **self.post_params,
            data=self.data,
        )

        self.assertEqual(response.status_code, 200)

        self.cert1.refresh_from_db()
        self.cert2.refresh_from_db()
        self.assertEqual(self.cert1.validated_by, ElecProvisionCertificateQualicharge.BOTH)
        self.assertEqual(self.cert2.validated_by, ElecProvisionCertificateQualicharge.BOTH)

        # An aggregated provision certificate should be created
        self.assertEqual(ElecProvisionCertificate.objects.count(), 1)

    def test_bulk_update_dgec_to_both(self):
        """Test updating from DGEC to BOTH (CPO validation)"""
        self.cert1.validated_by = ElecProvisionCertificateQualicharge.DGEC
        self.cert1.save()
        self.cert2.validated_by = ElecProvisionCertificateQualicharge.DGEC
        self.cert2.save()

        response = self.client.post(
            **self.post_params,
            data=self.data,
        )

        self.assertEqual(response.status_code, 200)

        self.cert1.refresh_from_db()
        self.cert2.refresh_from_db()
        self.assertEqual(self.cert1.validated_by, ElecProvisionCertificateQualicharge.BOTH)
        self.assertEqual(self.cert2.validated_by, ElecProvisionCertificateQualicharge.BOTH)

        # An aggregated provision certificate should be created
        self.assertEqual(ElecProvisionCertificate.objects.count(), 1)

    def test_bulk_update_already_both_error(self):
        """Test that a certificate already BOTH cannot be updated"""
        self.cert1.validated_by = ElecProvisionCertificateQualicharge.BOTH
        self.cert1.save()

        response = self.client.post(
            **self.post_params,
            data=self.data,
        )

        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("errors", json_response)
        self.assertTrue(len(json_response["errors"]) > 0)

        # Only cert2 should be updated
        self.cert1.refresh_from_db()
        self.cert2.refresh_from_db()
        self.assertEqual(self.cert1.validated_by, ElecProvisionCertificateQualicharge.BOTH)  # Unchanged
        self.assertEqual(self.cert2.validated_by, ElecProvisionCertificateQualicharge.CPO)  # Updated

    def test_bulk_update_no_certificates_found(self):
        """Test with non-existent certificate IDs"""
        self.data["certificate_ids"] = [99999]

        response = self.client.post(
            **self.post_params,
            data=self.data,
        )

        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        self.assertIn("No valid certificates found", json_response["errors"][0])

    def test_bulk_update_mixed_validation_states(self):
        """Test updating with mixed validation states"""
        self.cert1.validated_by = ElecProvisionCertificateQualicharge.NO_ONE
        self.cert1.save()
        self.cert2.validated_by = ElecProvisionCertificateQualicharge.CPO
        self.cert2.save()

        self.data["validated_by"] = ElecProvisionCertificateQualicharge.DGEC

        response = self.client.post(
            **self.post_params,
            data=self.data,
        )

        self.assertEqual(response.status_code, 200)

        self.cert1.refresh_from_db()
        self.cert2.refresh_from_db()
        # cert1 (NO_ONE) -> DGEC
        self.assertEqual(self.cert1.validated_by, ElecProvisionCertificateQualicharge.DGEC)
        # cert2 (CPO) + DGEC -> BOTH
        self.assertEqual(self.cert2.validated_by, ElecProvisionCertificateQualicharge.BOTH)
