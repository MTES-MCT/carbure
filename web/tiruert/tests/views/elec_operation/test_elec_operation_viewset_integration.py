from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from tiruert.models import ElecOperation


class ElecOperationViewSetIntegrationTest(TestCase):
    """Integration tests for ElecOperationViewSet CRUD operations."""

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
        self.list_url = reverse("elec-operations-list")

    def test_list_operations_filters_on_entity_and_returns_metadata(self):
        """GET /elec-operations/ should return only operations involving the entity."""
        response = self.client.get(self.list_url, {"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 3)  # excludes other_entity_operation
        self.assertEqual(data["total_quantity"], 350.0)  # 500 - 100 - 50

        types_by_id = {op["id"]: op["type"] for op in data["results"]}
        self.assertEqual(types_by_id[self.credit_operation.id], ElecOperation.ACQUISITION)
        self.assertEqual(types_by_id[self.debit_operation.id], ElecOperation.CESSION)

    def test_create_debit_operation_for_current_entity(self):
        """POST /elec-operations/ should create debit operations for the current entity."""
        payload = {
            "type": ElecOperation.CESSION,
            "debited_entity": self.entity.id,
            "credited_entity": self.counterparty.id,
            "quantity": 75.0,
        }

        response = self.client.post(
            self.list_url,
            data=payload,
            content_type="application/json",
            query_params={"entity_id": self.entity.id},
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["debited_entity"]["id"], self.entity.id)
        self.assertEqual(body["quantity"], 75.0)
        self.assertEqual(body["type"], ElecOperation.CESSION)

    def test_create_rejects_operations_not_debiting_current_entity(self):
        """Creation should fail when debited_entity differs from request.entity."""
        payload = {
            "type": ElecOperation.CESSION,
            "debited_entity": self.counterparty.id,
            "credited_entity": self.entity.id,
            "quantity": 10.0,
        }

        response = self.client.post(
            self.list_url,
            data=payload,
            content_type="application/json",
            query_params={"entity_id": self.entity.id},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Only debit operations can be created", str(response.json()))

    def test_partial_update_allows_editing_pending_debit_operations(self):
        """PATCH /elec-operations/:id/ should update pending debit operations."""
        url = reverse("elec-operations-detail", kwargs={"pk": self.debit_operation.id})
        payload = {"quantity": 200.0}

        response = self.client.patch(
            url,
            data=payload,
            content_type="application/json",
            query_params={"entity_id": self.entity.id},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["quantity"], 200.0)
        self.assertEqual(body["status"], ElecOperation.PENDING)

    def test_partial_update_rejects_operations_with_forbidden_status(self):
        """PATCH should return 400 when operation can no longer be modified."""
        operation = ElecOperation.objects.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.ACCEPTED,
            quantity=25.0,
            debited_entity=self.entity,
            credited_entity=self.counterparty,
        )
        url = reverse("elec-operations-detail", kwargs={"pk": operation.id})

        response = self.client.patch(
            url,
            data={"quantity": 30.0},
            content_type="application/json",
            query_params={"entity_id": self.entity.id},
        )

        self.assertEqual(response.status_code, 400)
        operation.refresh_from_db()
        self.assertEqual(operation.quantity, 25.0)

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
