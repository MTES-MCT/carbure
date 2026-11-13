from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Event
from unittest.mock import patch

from django.db import close_old_connections, connection
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from core.models import Biocarburant, Entity
from core.tests_utils import setup_current_user
from tiruert.factories import OperationFactory
from tiruert.factories.operation import OperationDetailFactory
from tiruert.models import Operation
from tiruert.services.correction import CorrectionService
from tiruert.views.operation.mixins.accept import AcceptActionMixin
from transactions.factories import CarbureLotFactory
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

    def test_declare_teneur_uses_corrected_flag_and_entity_scope(self):
        """Use the corrected flag, not detail deltas, while preserving entity scope."""
        operations = []
        corrected_and_delta = ((False, None), (True, None), (False, 0), (False, 5), (True, 5))
        for corrected, delta in corrected_and_delta:
            operation = OperationFactory(
                type=Operation.TENEUR,
                status=Operation.PENDING,
                debited_entity=self.entity,
                corrected=corrected,
            )
            OperationDetailFactory(operation=operation, emission_rate_per_mj_delta=delta)
            operations.append(operation)
        other = OperationFactory(
            type=Operation.TENEUR,
            status=Operation.PENDING,
            debited_entity=self.other_entity,
            corrected=True,
        )
        OperationDetailFactory(operation=other, emission_rate_per_mj_delta=5)

        response = self.client.post(reverse("operations-declare-teneur"), query_params=self.base_params)

        self.assertEqual(response.status_code, 200)
        expected_statuses = (
            Operation.DECLARED,
            Operation.CORRECTED,
            Operation.DECLARED,
            Operation.DECLARED,
            Operation.CORRECTED,
        )
        for operation, expected_status, (expected_corrected, _delta) in zip(
            operations, expected_statuses, corrected_and_delta
        ):
            operation.refresh_from_db()
            self.assertEqual(operation.status, expected_status)
            self.assertEqual(operation.corrected, expected_corrected)
        other.refresh_from_db()
        self.assertEqual(other.status, Operation.PENDING)
        self.assertTrue(other.corrected)

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


class DeclareTeneurCorrectionConcurrencyTest(TransactionTestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
    ]

    def test_declaration_and_ghg_correction_serialize_in_both_orders(self):
        """A simultaneous declaration and GHG correction always leave the teneur corrected."""
        if not connection.features.has_select_for_update:
            self.skipTest("The database backend does not support SELECT FOR UPDATE")

        entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        biofuel = Biocarburant.objects.get(code="ETH")
        setup_current_user(self, "concurrent@carbure.local", "Tester", "password", [(entity, "ADMIN")])

        for first, filter_feedstock in (
            ("correction", False),
            ("declaration", False),
            ("correction", True),
            ("declaration", True),
        ):
            with self.subTest(first=first, filter_feedstock=filter_feedstock):
                lot = CarbureLotFactory(biofuel=biofuel, ghg_total=20)
                credit = OperationFactory(
                    type=Operation.INCORPORATION, status=Operation.VALIDATED, biofuel=biofuel, credited_entity=entity
                )
                OperationDetailFactory(operation=credit, lot=lot, emission_rate_per_mj=20)
                teneur = OperationFactory(
                    type=Operation.TENEUR, status=Operation.PENDING, biofuel=biofuel, debited_entity=entity
                )
                OperationDetailFactory(operation=teneur, lot=lot, emission_rate_per_mj=20)
                lot.ghg_total = 25
                lot.save(update_fields=["ghg_total"])

                first_locked = Event()
                second_attempted = Event()
                second_unblocked = Event()
                release_first = Event()

                def worker(kind):
                    close_old_connections()

                    def intercept(execute, sql, params, many, context):
                        sql_upper = sql.upper()
                        if kind == first and sql_upper.startswith("UPDATE "):
                            table = "TIRUERT_OPERATION_DETAILS" if kind == "correction" else "TIRUERT_OPERATIONS"
                            if table in sql_upper and not first_locked.is_set():
                                if kind == "declaration":
                                    result = execute(sql, params, many, context)
                                first_locked.set()
                                if not release_first.wait(20):
                                    raise TimeoutError("Timed out waiting to release the first transaction")
                                if kind == "declaration":
                                    return result
                        if (
                            kind != first
                            and "TIRUERT_OPERATIONS" in sql_upper
                            and ("FOR UPDATE" in sql_upper or sql_upper.startswith("UPDATE "))
                        ):
                            second_attempted.set()
                            try:
                                return execute(sql, params, many, context)
                            finally:
                                second_unblocked.set()
                        return execute(sql, params, many, context)

                    try:
                        with connection.execute_wrapper(intercept):
                            if kind == "correction":
                                CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])
                            else:
                                params = {"entity_id": entity.id}
                                if filter_feedstock:
                                    params["feedstock"] = lot.feedstock.code
                                response = self.client.post(reverse("operations-declare-teneur"), query_params=params)
                                if response.status_code != 200:
                                    raise AssertionError(f"Declaration returned HTTP {response.status_code}")
                    finally:
                        connection.close()

                second = "declaration" if first == "correction" else "correction"
                with ThreadPoolExecutor(max_workers=2) as executor:
                    first_result = executor.submit(worker, first)
                    try:
                        self.assertTrue(first_locked.wait(10), "First transaction did not acquire its lock")
                        second_result = executor.submit(worker, second)
                        self.assertTrue(second_attempted.wait(10), "Second transaction did not start its database write")
                        self.assertFalse(second_unblocked.wait(0.2), "Second transaction did not wait for the first")
                    finally:
                        release_first.set()
                    first_result.result(timeout=15)
                    second_result.result(timeout=15)

                teneur.refresh_from_db()
                self.assertEqual(teneur.status, Operation.CORRECTED)
                self.assertTrue(teneur.corrected)
                self.assertEqual(teneur.details.get().emission_rate_per_mj_delta, 5)
