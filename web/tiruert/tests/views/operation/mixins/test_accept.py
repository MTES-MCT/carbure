from datetime import datetime
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from core.models import Biocarburant, Entity
from core.tests_utils import setup_current_user
from tiruert.factories import OperationFactory
from tiruert.models import Operation
from tiruert.views.operation.mixins.accept import AcceptActionMixin
from transactions.models import Depot


class AcceptActionMixinGetStatusAfterAcceptTest(TestCase):
    """Unit tests for AcceptActionMixin.get_status_after_accept() static method."""

    def test_get_status_after_accept_returns_correct_mapping(self):
        """Test get_status_after_accept returns correct status for each operation type."""
        # Define expected mappings
        expected_mappings = {
            Operation.CESSION: Operation.ACCEPTED,
            Operation.TRANSFERT: Operation.ACCEPTED,
            Operation.INCORPORATION: Operation.VALIDATED,
        }

        # Test all operation types
        for operation_type, _ in Operation.OPERATION_TYPES:
            with self.subTest(operation_type=operation_type):
                result = AcceptActionMixin.get_status_after_accept(operation_type)
                expected = expected_mappings.get(operation_type)
                self.assertEqual(
                    result,
                    expected,
                    f"{operation_type} should return {expected}, got {result}",
                )


class AcceptActionMixinTest(TestCase):
    """Integration tests for AcceptActionMixin.accept() action."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
        "json/entities_sites.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Set up test data shared across all test methods."""
        # Get references from fixtures
        cls.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        cls.other_entity = Entity.objects.filter(entity_type=Entity.OPERATOR).exclude(id=cls.entity.id).first()
        cls.depot = Depot.objects.first()
        cls.biofuel_eth = Biocarburant.objects.get(code="ETH")

    def setUp(self):
        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "password",
            [(self.entity, "ADMIN")],
        )

        self.base_params = {"entity_id": self.entity.id}

    @patch("tiruert.views.operation.mixins.accept.datetime")
    def test_accept_pending_operation_updates_status_and_validation_date(self, mock_datetime):
        """Test POST /operations/:id/accept/ updates status and sets validation_date."""
        mock_now = datetime(2025, 11, 20, 10, 30, 0)
        mock_datetime.now.return_value = mock_now

        operation = OperationFactory(
            type=Operation.CESSION,
            status=Operation.PENDING,
            debited_entity=self.entity,
            credited_entity=self.other_entity,
        )
        url = reverse("operations-accept", kwargs={"pk": operation.id})

        response = self.client.post(url, query_params=self.base_params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "accepted"})

        operation.refresh_from_db()
        self.assertEqual(operation.status, Operation.ACCEPTED)
        self.assertEqual(operation.validation_date, mock_now.date())

    def test_accept_only_allows_pending_status(self):
        """Test POST /operations/:id/accept/ only accepts PENDING operations, rejects all other statuses."""
        for status_value, _status_label in Operation.OPERATION_STATUSES:
            with self.subTest(status=status_value):
                operation = OperationFactory(
                    type=Operation.CESSION,
                    status=status_value,
                    debited_entity=self.entity,
                    credited_entity=self.other_entity,
                )
                url = reverse("operations-accept", kwargs={"pk": operation.id})

                if status_value == Operation.PENDING:
                    # PENDING should succeed
                    response = self.client.post(url, query_params=self.base_params)

                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json(), {"status": "accepted"})
                    operation.refresh_from_db()
                    self.assertEqual(operation.status, Operation.ACCEPTED)
                    self.assertIsNotNone(operation.validation_date)
                else:
                    # All other statuses should return 400
                    response = self.client.post(url, query_params=self.base_params)
                    self.assertEqual(response.status_code, 400)
                    self.assertEqual(response.json(), {"error": "OPERATION_ALREADY_ACCEPTED_VALIDATED"})
                    # Operation should not change
                    operation.refresh_from_db()
                    self.assertEqual(operation.status, status_value)

    @patch.object(AcceptActionMixin, "get_status_after_accept", return_value=None)
    def test_accept_returns_400_when_get_status_after_accept_returns_none(self, mock_get_status):
        """Test POST /operations/:id/accept/ returns 400 when get_status_after_accept returns None."""
        operation = OperationFactory(
            type=Operation.CESSION,
            status=Operation.PENDING,
            debited_entity=self.entity,
            credited_entity=self.other_entity,
        )
        url = reverse("operations-accept", kwargs={"pk": operation.id})

        response = self.client.post(url, query_params=self.base_params)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "OPERATION_TYPE_NOT_ALLOWED"})

        # Operation should not change
        operation.refresh_from_db()
        self.assertEqual(operation.status, Operation.PENDING)


class DeclareTeneurActionMixinTest(TestCase):
    """Integration tests for AcceptActionMixin.declare_teneur() action."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
        "json/entities_sites.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Set up test data shared across all test methods."""
        # Get references from fixtures
        cls.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        cls.other_entity = Entity.objects.filter(entity_type=Entity.OPERATOR).exclude(id=cls.entity.id).first()
        cls.depot = Depot.objects.first()
        cls.biofuel_eth = Biocarburant.objects.get(code="ETH")

    def setUp(self):
        """Set up test client for each test."""
        # Set up authenticated user
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "password", [(self.entity, "ADMIN")])
        self.base_params = {"entity_id": self.entity.id}

    def test_declare_teneur_changes_pending_operations_to_declared(self):
        """Test POST /operations/teneur/declare/ changes PENDING TENEUR operations to DECLARED."""
        # Create 3 PENDING TENEUR operations
        operation1 = OperationFactory(type=Operation.TENEUR, status=Operation.PENDING, credited_entity=self.entity)
        operation2 = OperationFactory(type=Operation.TENEUR, status=Operation.PENDING, credited_entity=self.entity)
        operation3 = OperationFactory(type=Operation.TENEUR, status=Operation.PENDING, credited_entity=self.entity)

        # Create 1 DECLARED TENEUR operation (should not be affected)
        operation4 = OperationFactory(type=Operation.TENEUR, status=Operation.DECLARED, credited_entity=self.entity)

        # Create 1 PENDING CESSION operation (should not be affected)
        operation5 = OperationFactory(
            type=Operation.CESSION,
            status=Operation.PENDING,
            credited_entity=self.entity,
            debited_entity=self.other_entity,
        )

        url = reverse("operations-declare-teneur")

        response = self.client.post(url, query_params=self.base_params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "declared"})

        # Verify only PENDING TENEUR operations were updated
        operation1.refresh_from_db()
        operation2.refresh_from_db()
        operation3.refresh_from_db()
        operation4.refresh_from_db()
        operation5.refresh_from_db()

        self.assertEqual(operation1.status, Operation.DECLARED)
        self.assertEqual(operation2.status, Operation.DECLARED)
        self.assertEqual(operation3.status, Operation.DECLARED)
        self.assertEqual(operation4.status, Operation.DECLARED)  # Unchanged
        self.assertEqual(operation5.status, Operation.PENDING)  # Unchanged

    def test_declare_teneur_with_no_pending_operations_returns_400(self):
        """Test POST /operations/teneur/declare/ returns 400 when no PENDING TENEUR operations exist."""
        # Create only DECLARED TENEUR operations
        OperationFactory(type=Operation.TENEUR, status=Operation.DECLARED, credited_entity=self.entity)

        url = reverse("operations-declare-teneur")

        response = self.client.post(url, query_params=self.base_params)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "NOTHING_TO_DECLARE"})

    def test_declare_teneur_with_no_operations_returns_400(self):
        """Test POST /operations/teneur/declare/ returns 400 when no TENEUR operations exist at all."""
        url = reverse("operations-declare-teneur")

        response = self.client.post(url, query_params=self.base_params)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "NOTHING_TO_DECLARE"})

    def test_declare_teneur_only_affects_filtered_entity(self):
        """Test POST /operations/teneur/declare/ only affects operations from the queried entity."""
        other_entity = Entity.objects.create(name="Other Entity", entity_type=Entity.OPERATOR)

        # Create PENDING TENEUR for main entity
        operation1 = OperationFactory(type=Operation.TENEUR, status=Operation.PENDING, credited_entity=self.entity)

        # Create PENDING TENEUR for other entity (should not be affected)
        operation2 = OperationFactory(type=Operation.TENEUR, status=Operation.PENDING, credited_entity=other_entity)

        url = reverse("operations-declare-teneur")

        response = self.client.post(url, query_params=self.base_params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "declared"})

        # Verify only main entity's operation was updated
        operation1.refresh_from_db()
        operation2.refresh_from_db()

        self.assertEqual(operation1.status, Operation.DECLARED)
        self.assertEqual(operation2.status, Operation.PENDING)  # Unchanged
