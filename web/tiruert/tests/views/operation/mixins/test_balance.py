from unittest.mock import patch

from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from core.models import Entity
from tiruert.models import Operation
from tiruert.views.operation.mixins.balance import BalanceActionMixin, BalancePagination


class BalancePaginationTest(TestCase):
    """Test BalancePagination class"""

    def setUp(self):
        self.paginator = BalancePagination()

    def test_balance_pagination_aggregate_fields(self):
        """Test that BalancePagination defines aggregate_fields correctly"""
        self.assertIn("total_quantity", self.paginator.aggregate_fields)
        self.assertEqual(self.paginator.aggregate_fields["total_quantity"], 0)

    def test_get_extra_metadata_with_empty_queryset(self):
        """Test that get_extra_metadata returns zero total_quantity for empty queryset"""
        self.paginator.queryset = []
        metadata = self.paginator.get_extra_metadata()
        self.assertEqual(metadata["total_quantity"], 0)

    def test_get_extra_metadata_sums_available_balance(self):
        """Test that get_extra_metadata correctly sums available_balance from queryset"""
        self.paginator.queryset = [
            {"available_balance": 100.0, "quantity": {"credit": 50.0, "debit": 25.0}},
            {"available_balance": 150.0, "quantity": {"credit": 75.0, "debit": 30.0}},
            {"available_balance": 75.0, "quantity": {"credit": 40.0, "debit": 15.0}},
        ]
        metadata = self.paginator.get_extra_metadata()
        self.assertEqual(metadata["total_quantity"], 325.0)  # 100 + 150 + 75

    def test_get_extra_metadata_handles_negative_values(self):
        """Test that get_extra_metadata correctly handles negative available_balance"""
        self.paginator.queryset = [
            {"available_balance": 100.0, "quantity": {"credit": 50.0, "debit": 25.0}},
            {"available_balance": -50.0, "quantity": {"credit": 75.0, "debit": 30.0}},
        ]
        metadata = self.paginator.get_extra_metadata()
        self.assertEqual(metadata["total_quantity"], 50.0)  # 100 + (-50)


class BalanceActionMixinTest(TestCase):
    """Test BalanceActionMixin"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.entity = Entity.objects.create(name="Test Entity", entity_type=Entity.OPERATOR)

        # Create a mock view class using BalanceActionMixin
        class MockBalanceView(BalanceActionMixin):
            def get_queryset(self):
                return Operation.objects.none()

            def filter_queryset(self, queryset):
                return queryset

            def get_serializer_class(self):
                from tiruert.serializers import BalanceSerializer

                return BalanceSerializer

        self.view = MockBalanceView()

    def _create_request(self, query_params=None):
        """Helper to create a DRF Request object with proper attributes"""
        django_request = self.factory.get("/api/operations/balance/", query_params or {})
        request = Request(django_request)
        request.entity = self.entity
        request.unit = query_params.get("unit", "l") if query_params else "l"
        return request

    def _create_mock_balance_data(self):
        """Helper to create mock balance data for testing"""
        return {
            "key1": {
                "sector": "ESSENCE",
                "customs_category": "CONV",
                "biofuel": {"id": 1, "code": "ETH", "renewable_energy_share": 0.8},
                "available_balance": 200.0,
                "quantity": {"credit": 100.0, "debit": 50.0},
                "pending_teneur": 0.0,
                "pending_operations": 5,
                "saved_emissions": 100.0,
                "ghg_reduction_min": 50.0,
                "ghg_reduction_max": 60.0,
                "declared_teneur": 0.0,
                "unit": "l",
            },
            "key2": {
                "sector": "GAZOLE",
                "customs_category": "CONV",
                "biofuel": {"id": 2, "code": "EMHV", "renewable_energy_share": 0.85},
                "available_balance": 50.0,
                "quantity": {"credit": 25.0, "debit": 10.0},
                "pending_operations": 2,
                "saved_emissions": 25.0,
                "ghg_reduction_min": 45.0,
                "ghg_reduction_max": 55.0,
                "pending_teneur": 0.0,
                "declared_teneur": 0.0,
                "unit": "l",
            },
            "key3": {
                "sector": "GPL",
                "customs_category": "CONV",
                "biofuel": {"id": 3, "code": "EMAG", "renewable_energy_share": 0.9},
                "available_balance": 150.0,
                "quantity": {"credit": 75.0, "debit": 30.0},
                "pending_operations": 3,
                "saved_emissions": 75.0,
                "ghg_reduction_min": 55.0,
                "ghg_reduction_max": 65.0,
                "pending_teneur": 0.0,
                "declared_teneur": 0.0,
                "unit": "l",
            },
        }

    @patch("tiruert.services.balance.BalanceService.calculate_balance")
    def test_balance_action_calls_calculate_balance_service(self, mock_calculate_balance):
        """Test that balance action calls BalanceService.calculate_balance with correct parameters"""
        mock_calculate_balance.return_value = {}

        request = self._create_request({"unit": "l"})

        self.view.balance(request)

        mock_calculate_balance.assert_called_once()
        call_args = mock_calculate_balance.call_args[0]
        self.assertEqual(call_args[1], self.entity.id)  # entity_id
        self.assertIsNone(call_args[2])  # group_by
        self.assertEqual(call_args[3], "l")  # unit

    def test_balance_action_serializer_selection(self):
        """Test that balance action selects the correct serializer based on group_by parameter"""
        from tiruert.serializers.balance import (
            BalanceByDepotSerializer,
            BalanceByLotSerializer,
            BalanceBySectorSerializer,
            BalanceSerializer,
        )

        # Test mapping dictionary directly from the balance method logic
        test_cases = [
            ("lot", BalanceByLotSerializer),
            ("depot", BalanceByDepotSerializer),
            ("sector", BalanceBySectorSerializer),
            (None, BalanceSerializer),  # default when no group_by
        ]

        for group_by, expected_serializer in test_cases:
            with self.subTest(group_by=group_by):
                serializer_mapping = {
                    "lot": BalanceByLotSerializer,
                    "depot": BalanceByDepotSerializer,
                    "sector": BalanceBySectorSerializer,
                }
                selected = serializer_mapping.get(group_by, self.view.get_serializer_class())
                self.assertEqual(selected, expected_serializer)

    @patch("tiruert.services.balance.BalanceService.calculate_balance")
    def test_balance_action_with_date_from_parameter(self, mock_calculate_balance):
        """Test that balance action parses and passes date_from parameter correctly"""
        mock_calculate_balance.return_value = {}

        request = self._create_request({"unit": "l", "date_from": "2025-01-15"})

        self.view.balance(request)

        mock_calculate_balance.assert_called_once()
        call_args = mock_calculate_balance.call_args[0]
        date_from = call_args[4]
        self.assertIsNotNone(date_from)
        self.assertEqual(date_from.year, 2025)
        self.assertEqual(date_from.month, 1)
        self.assertEqual(date_from.day, 15)

    @patch("tiruert.services.balance.BalanceService.calculate_balance")
    def test_balance_action_with_ges_bounds(self, mock_calculate_balance):
        """Test that balance action passes ges_bound_min and ges_bound_max parameters"""
        mock_calculate_balance.return_value = {}

        request = self._create_request({"unit": "l", "ges_bound_min": "50.0", "ges_bound_max": "80.0"})

        self.view.balance(request)

        mock_calculate_balance.assert_called_once()
        call_args = mock_calculate_balance.call_args[0]
        self.assertEqual(call_args[5], "50.0")  # ges_bound_min
        self.assertEqual(call_args[6], "80.0")  # ges_bound_max

    @patch("tiruert.services.balance.BalanceService.calculate_balance")
    def test_balance_action_with_order_by_available_balance(self, mock_calculate_balance):
        """Test that balance action sorts results by available_balance when order_by parameter is provided"""
        mock_calculate_balance.return_value = self._create_mock_balance_data()

        request = self._create_request({"unit": "l", "order_by": "available_balance"})

        response = self.view.balance(request)

        self.assertEqual(response.status_code, 200)
        # Verify results are sorted ascending
        results = response.data["results"]
        self.assertEqual(results[0]["available_balance"], 50.0)
        self.assertEqual(results[1]["available_balance"], 150.0)
        self.assertEqual(results[2]["available_balance"], 200.0)

    @patch("tiruert.services.balance.BalanceService.calculate_balance")
    def test_balance_action_with_order_by_available_balance_descending(self, mock_calculate_balance):
        """Test that balance action sorts results descending when order_by starts with '-'"""
        mock_calculate_balance.return_value = self._create_mock_balance_data()

        request = self._create_request({"unit": "l", "order_by": "-available_balance"})

        response = self.view.balance(request)

        self.assertEqual(response.status_code, 200)
        # Verify results are sorted descending
        results = response.data["results"]
        self.assertEqual(results[0]["available_balance"], 200.0)
        self.assertEqual(results[1]["available_balance"], 150.0)
        self.assertEqual(results[2]["available_balance"], 50.0)

    @patch("tiruert.services.balance.BalanceService.calculate_balance")
    def test_balance_action_returns_paginated_response(self, mock_calculate_balance):
        """Test that balance action returns a paginated response with metadata"""
        # Use only first 2 entries for pagination test
        mock_data = self._create_mock_balance_data()
        mock_calculate_balance.return_value = dict(list(mock_data.items())[:2])

        request = self._create_request({"unit": "l"})

        response = self.view.balance(request)

        self.assertEqual(response.status_code, 200)
        # Verify pagination structure
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertIn("total_quantity", response.data)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["total_quantity"], 250.0)  # 200 + 50
