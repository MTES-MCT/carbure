from unittest.mock import Mock

from django.test import TestCase

from tiruert.models import ElecOperation
from tiruert.views.elec_operation.elec_operation import ElecOperationPagination


class ElecOperationPaginationTest(TestCase):
    """Tests for ElecOperationPagination.get_extra_metadata()."""

    def setUp(self):
        self.pagination = ElecOperationPagination()
        self.pagination.request = Mock()
        self.pagination.request.entity = Mock()
        self.pagination.request.entity.id = 42

    def test_get_extra_metadata_with_empty_queryset(self):
        """Should return zero when there are no operations."""
        self.pagination.queryset = []

        result = self.pagination.get_extra_metadata()

        self.assertEqual(result, {"total_quantity": 0})

    def test_get_extra_metadata_counts_credit_operations(self):
        """Should sum positive quantity for credit operations."""
        operation = Mock()
        operation.is_credit.return_value = True
        operation.quantity = 150.0
        operation.status = ElecOperation.ACCEPTED

        self.pagination.queryset = [operation]

        result = self.pagination.get_extra_metadata()

        operation.is_credit.assert_called_once_with(42)
        self.assertEqual(result["total_quantity"], 150.0)

    def test_get_extra_metadata_counts_debit_operations_as_negative(self):
        """Should subtract quantity for debit operations."""
        operation = Mock()
        operation.is_credit.return_value = False
        operation.quantity = 75.0
        operation.status = ElecOperation.PENDING

        self.pagination.queryset = [operation]

        result = self.pagination.get_extra_metadata()

        operation.is_credit.assert_called_once_with(42)
        self.assertEqual(result["total_quantity"], -75.0)

    def test_get_extra_metadata_ignores_rejected_operations(self):
        """Rejected operations should not affect the total."""
        operation = Mock()
        operation.is_credit.return_value = True
        operation.quantity = 500.0
        operation.status = ElecOperation.REJECTED

        self.pagination.queryset = [operation]

        result = self.pagination.get_extra_metadata()

        self.assertEqual(result["total_quantity"], 0)

    def test_get_extra_metadata_mixed_operations(self):
        """Should compute net quantity across mixed operations."""
        credit = Mock()
        credit.is_credit.return_value = True
        credit.quantity = 200.0
        credit.status = ElecOperation.ACCEPTED

        debit = Mock()
        debit.is_credit.return_value = False
        debit.quantity = 50.0
        debit.status = ElecOperation.PENDING

        rejected = Mock()
        rejected.is_credit.return_value = True
        rejected.quantity = 100.0
        rejected.status = ElecOperation.REJECTED

        self.pagination.queryset = [credit, debit, rejected]

        result = self.pagination.get_extra_metadata()

        self.assertEqual(result["total_quantity"], 150.0)
