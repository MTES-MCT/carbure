from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from tiruert.factories import ElecOperationFactory
from tiruert.models import ElecOperation
from tiruert.views.elec_operation.mixins.accept import AcceptActionMixinErrors


class ElecAcceptActionMixinTest(TestCase):
    """Integration tests for AcceptActionMixin.accept()."""

    @classmethod
    def setUpTestData(cls):
        cls.entity = Entity.objects.create(name="Elec Operator", entity_type=Entity.OPERATOR, has_elec=True)
        cls.other_entity = Entity.objects.create(name="Counterparty", entity_type=Entity.OPERATOR, has_elec=True)

    def setUp(self):
        setup_current_user(self, "user@carbure.local", "User", "password", [(self.entity, "ADMIN")])

    def test_accept_pending_cession_sets_status_accepted(self):
        """POST /elec-operations/:id/accept/ should accept pending cesssion."""
        operation = ElecOperationFactory(
            type=ElecOperation.CESSION,
            status=ElecOperation.PENDING,
            debited_entity=self.entity,
            credited_entity=self.other_entity,
        )
        url = reverse("elec-operations-accept", kwargs={"pk": operation.id})

        response = self.client.post(url, query_params={"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "accepted"})
        operation.refresh_from_db()
        self.assertEqual(operation.status, ElecOperation.ACCEPTED)

    def test_accept_rejects_non_pending_statuses(self):
        """Only PENDING operations can be accepted."""
        forbidden_statuses = [
            ElecOperation.ACCEPTED,
            ElecOperation.REJECTED,
            ElecOperation.CANCELED,
            ElecOperation.DECLARED,
        ]

        for status in forbidden_statuses:
            with self.subTest(status=status):
                operation = ElecOperationFactory(
                    type=ElecOperation.CESSION,
                    status=status,
                    debited_entity=self.entity,
                    credited_entity=self.other_entity,
                )
                url = reverse("elec-operations-accept", kwargs={"pk": operation.id})

                response = self.client.post(url, query_params={"entity_id": self.entity.id})

                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {"error": AcceptActionMixinErrors.OPERATION_ALREADY_ACCEPTED_VALIDATED})
                operation.refresh_from_db()
                self.assertEqual(operation.status, status)

    def test_accept_rejects_disallowed_operation_types(self):
        """Accept should return 400 for non-cession operations."""
        operation = ElecOperationFactory.create_teneur(self.entity, status=ElecOperation.PENDING, quantity=10)
        url = reverse("elec-operations-accept", kwargs={"pk": operation.id})

        response = self.client.post(url, query_params={"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": AcceptActionMixinErrors.OPERATION_TYPE_NOT_ALLOWED})
        operation.refresh_from_db()
        self.assertEqual(operation.status, ElecOperation.PENDING)


class ElecDeclareTeneurActionMixinTest(TestCase):
    """Integration tests for AcceptActionMixin.declare_teneur()."""

    @classmethod
    def setUpTestData(cls):
        cls.entity = Entity.objects.create(name="Elec Operator", entity_type=Entity.OPERATOR, has_elec=True)
        cls.other_entity = Entity.objects.create(name="Other Operator", entity_type=Entity.OPERATOR, has_elec=True)

    def setUp(self):
        setup_current_user(self, "user@carbure.local", "User", "password", [(self.entity, "ADMIN")])

    def test_declare_teneur_updates_only_pending_operations(self):
        """POST /elec-operations/teneur/declare/ should declare pending teneur for the entity."""
        op1 = ElecOperationFactory.create_teneur(self.entity, status=ElecOperation.PENDING, quantity=10)
        op2 = ElecOperationFactory.create_teneur(self.entity, status=ElecOperation.PENDING, quantity=20)
        op3 = ElecOperationFactory.create_teneur(self.entity, status=ElecOperation.DECLARED, quantity=30)
        other = ElecOperationFactory.create_teneur(self.other_entity, status=ElecOperation.PENDING, quantity=40)

        url = reverse("elec-operations-declare-teneur")

        response = self.client.post(url, query_params={"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "declared"})

        op1.refresh_from_db()
        op2.refresh_from_db()
        op3.refresh_from_db()
        other.refresh_from_db()

        self.assertEqual(op1.status, ElecOperation.DECLARED)
        self.assertEqual(op2.status, ElecOperation.DECLARED)
        self.assertEqual(op3.status, ElecOperation.DECLARED)
        self.assertEqual(other.status, ElecOperation.PENDING)

    def test_declare_teneur_returns_error_when_nothing_to_declare(self):
        """Should return 400 when there are no pending teneur operations."""
        ElecOperationFactory.create_teneur(self.entity, status=ElecOperation.DECLARED, quantity=10)
        url = reverse("elec-operations-declare-teneur")

        response = self.client.post(url, query_params={"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": AcceptActionMixinErrors.NOTHING_TO_DECLARE})
