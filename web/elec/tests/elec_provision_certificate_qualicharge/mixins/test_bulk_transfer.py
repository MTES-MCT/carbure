from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from elec.factories import ElecProvisionCertificateQualichargeFactory
from elec.models import ElecProvisionCertificateQualicharge
from entity.factories import EntityFactory


class BulkTransferMixinTest(TestCase):
    """Integration tests for the bulk transfer mixin."""

    def setUp(self):
        self.parent_cpo = EntityFactory.create(
            name="Parent CPO",
            entity_type=Entity.CPO,
        )

        self.child_cpo = EntityFactory.create(
            name="Child CPO",
            entity_type=Entity.CPO,
            parent_entity=self.parent_cpo,
        )

        self.other_cpo = EntityFactory.create(
            name="Other CPO",
            entity_type=Entity.CPO,
        )

        self.cert1 = ElecProvisionCertificateQualichargeFactory.create(
            cpo=self.parent_cpo,
            operating_unit="FR001",
            station_id="FRXYZP111111",
            energy_amount=1000.0,
            validated_by=ElecProvisionCertificateQualicharge.NO_ONE,
        )

        self.cert2 = ElecProvisionCertificateQualichargeFactory.create(
            cpo=self.parent_cpo,
            operating_unit="FR001",
            station_id="FRXYZP222222",
            energy_amount=2000.0,
            validated_by=ElecProvisionCertificateQualicharge.NO_ONE,
        )

        self.cert_both_validated = ElecProvisionCertificateQualichargeFactory.create(
            cpo=self.parent_cpo,
            operating_unit="FR001",
            station_id="FRXYZP333333",
            energy_amount=500.0,
            validated_by=ElecProvisionCertificateQualicharge.BOTH,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.parent_cpo, "RW")],
        )

    # --- transfer-targets ---

    def test_transfer_targets_returns_child_cpos(self):
        """transfer-targets returns CPOs whose parent_entity is the current entity."""
        response = self.client.get(
            reverse("elec-provision-certificate-qualicharge-transfer-targets"),
            {"entity_id": self.parent_cpo.id},
        )
        self.assertEqual(response.status_code, 200)
        ids = [e["id"] for e in response.json()]
        self.assertIn(self.child_cpo.id, ids)
        self.assertNotIn(self.other_cpo.id, ids)
        self.assertNotIn(self.parent_cpo.id, ids)

    def test_transfer_targets_empty_when_no_children(self):
        """transfer-targets returns an empty list when there are no child CPOs."""
        setup_current_user(
            self,
            "other@carbure.local",
            "Other",
            "gogogo",
            [(self.other_cpo, "RW")],
        )
        response = self.client.get(
            reverse("elec-provision-certificate-qualicharge-transfer-targets"),
            {"entity_id": self.other_cpo.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    # --- bulk-transfer ---

    def test_bulk_transfer_success(self):
        """Certificates not double-validated are reassigned to the target child CPO."""
        response = self.client.post(
            reverse("elec-provision-certificate-qualicharge-bulk-transfer"),
            data={
                "operating_unit": ["FR001"],
                "target_cpo_id": self.child_cpo.id,
            },
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.parent_cpo.id}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

        self.cert1.refresh_from_db()
        self.cert2.refresh_from_db()
        self.assertEqual(self.cert1.cpo, self.child_cpo)
        self.assertEqual(self.cert1.validated_by, ElecProvisionCertificateQualicharge.NO_ONE)
        self.assertEqual(self.cert2.cpo, self.child_cpo)

    def test_bulk_transfer_excludes_both_validated(self):
        """Certificates validated by BOTH are not transferred."""
        response = self.client.post(
            reverse("elec-provision-certificate-qualicharge-bulk-transfer"),
            data={
                "operating_unit": ["FR001"],
                "target_cpo_id": self.child_cpo.id,
            },
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.parent_cpo.id}",
        )
        self.assertEqual(response.status_code, 200)

        self.cert_both_validated.refresh_from_db()
        self.assertEqual(self.cert_both_validated.cpo, self.parent_cpo)

    def test_bulk_transfer_no_certificates_found(self):
        """Returns 400 when no transferable certificates match the operating unit."""
        response = self.client.post(
            reverse("elec-provision-certificate-qualicharge-bulk-transfer"),
            data={
                "operating_unit": ["UNKNOWN_UNIT"],
                "target_cpo_id": self.child_cpo.id,
            },
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.parent_cpo.id}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")

    def test_bulk_transfer_unauthorized_target_cpo(self):
        """Returns 400 when target CPO is not a child of the current entity."""
        response = self.client.post(
            reverse("elec-provision-certificate-qualicharge-bulk-transfer"),
            data={
                "operating_unit": ["FR001"],
                "target_cpo_id": self.other_cpo.id,
            },
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.parent_cpo.id}",
        )
        self.assertEqual(response.status_code, 400)

    def test_bulk_transfer_target_cpo_not_found(self):
        """Returns 400 when target CPO does not exist."""
        response = self.client.post(
            reverse("elec-provision-certificate-qualicharge-bulk-transfer"),
            data={
                "operating_unit": ["FR001"],
                "target_cpo_id": 99999,
            },
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.parent_cpo.id}",
        )
        self.assertEqual(response.status_code, 400)
