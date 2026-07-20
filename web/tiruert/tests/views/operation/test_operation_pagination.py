from unittest.mock import Mock

from django.test import TestCase

from tiruert.views.operation.operation import OperationPagination


class OperationPaginationTest(TestCase):
    """Tests for OperationPagination.get_extra_metadata()."""

    def setUp(self):
        self.pagination = OperationPagination()
        self.pagination.request = Mock()
        self.pagination.request.entity = Mock()
        self.pagination.request.entity.id = 100

    def test_get_extra_metadata_empty_queryset(self):
        """Should return zero total_quantity for empty queryset."""
        self.pagination.queryset = []

        result = self.pagination.get_extra_metadata()

        self.assertEqual(result, {"total_quantity": 0.0})

    def test_get_extra_metadata_single_credit_operation(self):
        """Should return positive quantity for credit operation."""
        # Create mock operation
        operation = Mock()
        operation._volume = 1000.0
        operation.renewable_energy_share = 1.0

        self.pagination.queryset = [operation]

        result = self.pagination.get_extra_metadata()

        self.assertEqual(result["total_quantity"], 1000.0)

    def test_get_extra_metadata_single_debit_operation(self):
        """Should return negative quantity for debit operation."""
        operation = Mock()
        operation._volume = -1000.0
        operation.renewable_energy_share = 1.0

        self.pagination.queryset = [operation]

        result = self.pagination.get_extra_metadata()

        self.assertEqual(result["total_quantity"], -1000.0)

    def test_get_extra_metadata_mixed_operations(self):
        """Should calculate net quantity for mixed credit/debit operations."""
        credit_op = Mock()
        credit_op._volume = 1000.0
        credit_op.renewable_energy_share = 1.0

        debit_op = Mock()
        debit_op._volume = -500.0
        debit_op.renewable_energy_share = 1.0

        self.pagination.queryset = [credit_op, debit_op]

        result = self.pagination.get_extra_metadata()

        self.assertEqual(result["total_quantity"], 500.0)

    def test_get_extra_metadata_with_renewable_energy_share(self):
        """Should apply renewable_energy_share to volume calculation."""
        operation = Mock()
        operation._volume = 1000.0
        operation.renewable_energy_share = 0.5

        self.pagination.queryset = [operation]

        result = self.pagination.get_extra_metadata()

        # Should multiply signed volume by renewable_energy_share
        self.assertEqual(result["total_quantity"], 500.0)

    def test_get_extra_metadata_multiple_operations_complex(self):
        """Should correctly sum multiple operations with different shares and signs."""
        # Credit operation with 100% renewable
        op1 = Mock()
        op1._volume = 1000.0
        op1.renewable_energy_share = 1.0

        # Credit operation with 60% renewable
        op2 = Mock()
        op2._volume = 1000.0
        op2.renewable_energy_share = 0.6

        # Debit operation with 100% renewable
        op3 = Mock()
        op3._volume = -800.0
        op3.renewable_energy_share = 1.0

        self.pagination.queryset = [op1, op2, op3]

        result = self.pagination.get_extra_metadata()

        # Expected: 1000*1.0 + 1000*0.6 + (-800)*1.0 = 800
        self.assertEqual(result["total_quantity"], 800.0)

    def test_get_extra_metadata_zero_renewable_energy_share(self):
        """Should handle zero renewable_energy_share."""
        operation = Mock()
        operation._volume = 1000.0
        operation.renewable_energy_share = 0.0

        self.pagination.queryset = [operation]

        result = self.pagination.get_extra_metadata()

        self.assertEqual(result["total_quantity"], 0.0)

    def test_get_extra_metadata_uses_queryset_aggregate_when_available(self):
        """Should delegate total_quantity computation to the ORM queryset when possible."""
        queryset = Mock()
        queryset.aggregate.return_value = {"total_quantity": 1234.5}
        self.pagination.queryset = queryset

        result = self.pagination.get_extra_metadata()

        queryset.aggregate.assert_called_once()
        self.assertEqual(result, {"total_quantity": 1234.5})
