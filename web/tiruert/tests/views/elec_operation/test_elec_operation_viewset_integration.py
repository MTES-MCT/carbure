from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from tiruert.models import ElecOperation


class ElecOperationViewSetIntegrationTest(TestCase):
    """Integration tests for ElecOperationViewSet covering view-only rules."""

    @classmethod
    def setUpTestData(cls):
        cls.entity = Entity.objects.create(name="Elec Operator", entity_type=Entity.OPERATOR, has_elec=True)
        cls.counterparty = Entity.objects.create(name="Counterparty", entity_type=Entity.OPERATOR, has_elec=True)
        cls.other_entity = Entity.objects.create(name="Other Operator", entity_type=Entity.OPERATOR, has_elec=True)

        # Credit operation (will be shown as ACQUISITION for the entity)
        cls.credit_operation = ElecOperation.objects.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.ACCEPTED,
            quantity=500,
            credited_entity=cls.entity,
            debited_entity=cls.counterparty,
        )
        # Debit operation
        cls.debit_operation = ElecOperation.objects.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.PENDING,
            quantity=100,
            debited_entity=cls.entity,
            credited_entity=cls.counterparty,
        )
        # Pending teneur
        cls.teneur_operation = ElecOperation.objects.create(
            type=ElecOperation.TENEUR,
            status=ElecOperation.PENDING,
            quantity=50,
            debited_entity=cls.entity,
        )
        # Operation for another entity (should be excluded by filters)
        cls.other_entity_operation = ElecOperation.objects.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.ACCEPTED,
            quantity=999,
            credited_entity=cls.other_entity,
            debited_entity=cls.counterparty,
        )

    def setUp(self):
        setup_current_user(self, "user@carbure.local", "User", "password", [(self.entity, "ADMIN")])

    def test_destroy_allows_pending_cession(self):
        """DELETE /elec-operations/:id/ should delete allowed operations."""
        operation = ElecOperation.objects.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.PENDING,
            quantity=10.0,
            debited_entity=self.entity,
            credited_entity=self.counterparty,
        )
        url = reverse("elec-operations-detail", kwargs={"pk": operation.id})

        response = self.client.delete(url, query_params={"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 204)
        self.assertFalse(ElecOperation.objects.filter(id=operation.id).exists())

    def test_destroy_rejects_disallowed_type(self):
        """DELETE should return 403 for disallowed operation types."""
        operation = ElecOperation.objects.create(
            type=ElecOperation.ACQUISITION_FROM_CPO,
            status=ElecOperation.PENDING,
            quantity=10.0,
            credited_entity=self.entity,
        )
        url = reverse("elec-operations-detail", kwargs={"pk": operation.id})

        response = self.client.delete(url, query_params={"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 403)
        self.assertTrue(ElecOperation.objects.filter(id=operation.id).exists())

    def test_destroy_rejects_disallowed_status(self):
        """DELETE should return 403 when status is not deletable."""
        operation = ElecOperation.objects.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.ACCEPTED,
            quantity=10.0,
            debited_entity=self.entity,
            credited_entity=self.counterparty,
        )
        url = reverse("elec-operations-detail", kwargs={"pk": operation.id})

        response = self.client.delete(url, query_params={"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 403)
        self.assertTrue(ElecOperation.objects.filter(id=operation.id).exists())
