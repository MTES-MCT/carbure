from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from tiruert.factories import OperationFactory
from tiruert.models import Operation


class RejectActionMixinTest(TestCase):
    """Integration tests for RejectActionMixin.reject() action."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/depots.json",
        "json/entities_sites.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Set up test data shared across all test methods."""
        # Get references from fixtures
        cls.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        cls.other_entity = Entity.objects.filter(entity_type=Entity.OPERATOR).exclude(id=cls.entity.id).first()

    def setUp(self):
        """Set up test client for each test."""
        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "password",
            [(self.entity, "ADMIN")],
        )
        self.base_params = {"entity_id": self.entity.id}

    def test_reject_operation_updates_status_to_rejected(self):
        """Test POST /operations/:id/reject/ changes operation status to REJECTED."""
        operation = OperationFactory(
            type=Operation.CESSION,
            status=Operation.PENDING,
            debited_entity=self.entity,
            credited_entity=self.other_entity,
        )
        url = reverse("operations-reject", kwargs={"pk": operation.id})

        response = self.client.post(url, query_params=self.base_params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "rejected"})

        operation.refresh_from_db()
        self.assertEqual(operation.status, Operation.REJECTED)
