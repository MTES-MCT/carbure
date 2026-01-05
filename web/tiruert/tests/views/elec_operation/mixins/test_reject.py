from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from tiruert.factories import ElecOperationFactory
from tiruert.models import ElecOperation


class ElecRejectActionMixinTest(TestCase):
    """Integration tests for RejectActionMixin.reject()."""

    @classmethod
    def setUpTestData(cls):
        cls.entity = Entity.objects.create(name="Elec Operator", entity_type=Entity.OPERATOR, has_elec=True)
        cls.other_entity = Entity.objects.create(name="Counterparty", entity_type=Entity.OPERATOR, has_elec=True)

    def setUp(self):
        setup_current_user(self, "user@carbure.local", "User", "password", [(self.entity, "ADMIN")])

    def test_reject_operation_sets_status_rejected(self):
        """POST /elec-operations/:id/reject/ should set status to REJECTED."""
        operation = ElecOperationFactory(
            type=ElecOperation.CESSION,
            status=ElecOperation.PENDING,
            debited_entity=self.entity,
            credited_entity=self.other_entity,
        )
        url = reverse("elec-operations-reject", kwargs={"pk": operation.id})

        response = self.client.post(url, query_params={"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "rejected"})
        operation.refresh_from_db()
        self.assertEqual(operation.status, ElecOperation.REJECTED)
