from unittest.mock import patch

from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from core.models import Entity
from tiruert.models import ElecOperation
from tiruert.views.elec_operation.mixins.balance import BalanceActionMixin, ElecBalancePagination


class ElecBalancePaginationTest(TestCase):
    """Tests for ElecBalancePagination.get_extra_metadata()."""

    def setUp(self):
        self.paginator = ElecBalancePagination()

    def test_aggregate_fields(self):
        """Paginator should expose aggregate_fields with total_quantity."""
        self.assertIn("total_quantity", self.paginator.aggregate_fields)
        self.assertEqual(self.paginator.aggregate_fields["total_quantity"], 0)

    def test_get_extra_metadata_with_empty_queryset(self):
        """Returns zero total_quantity when queryset is empty."""
        self.paginator.queryset = []

        metadata = self.paginator.get_extra_metadata()

        self.assertEqual(metadata["total_quantity"], 0)

    def test_get_extra_metadata_sums_available_balance(self):
        """Sums available_balance across items."""
        self.paginator.queryset = [
            {"available_balance": 100.0},
            {"available_balance": -25.5},
            {"available_balance": 10.0},
        ]

        metadata = self.paginator.get_extra_metadata()

        self.assertEqual(metadata["total_quantity"], 84.5)


class ElecBalanceActionMixinTest(TestCase):
    """Tests for BalanceActionMixin.balance()."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.entity = Entity.objects.create(name="Elec Operator", entity_type=Entity.OPERATOR, has_elec=True)

        class MockBalanceView(BalanceActionMixin):
            def get_queryset(self):
                return ElecOperation.objects.none()

            def filter_queryset(self, queryset):
                return queryset

        self.view = MockBalanceView()

    def _make_request(self, params=None):
        django_request = self.factory.get("/elec-operations/balance/", params or {})
        request = Request(django_request)
        request.entity = self.entity
        return request

    @patch("tiruert.services.elec_balance.ElecBalanceService.calculate_balance")
    def test_balance_parses_date_and_calls_service(self, mock_calculate_balance):
        """Should pass parsed date_from and entity_id to service."""
        mock_calculate_balance.return_value = {
            "sector": ElecOperation.SECTOR,
            "quantity": {"credit": 0, "debit": 0},
            "available_balance": 0,
            "pending_teneur": 0,
            "declared_teneur": 0,
            "pending_operations": 0,
            "emission_rate_per_mj": ElecOperation.EMISSION_RATE_PER_MJ,
        }
        request = self._make_request({"date_from": "2025-01-15"})

        self.view.balance(request)

        self.assertTrue(mock_calculate_balance.called)
        _, entity_id, date_from = mock_calculate_balance.call_args[0]
        self.assertEqual(entity_id, self.entity.id)
        self.assertIsNotNone(date_from)
        self.assertEqual(date_from.year, 2025)
        self.assertEqual(date_from.month, 1)
        self.assertEqual(date_from.day, 15)

    @patch("tiruert.services.elec_balance.ElecBalanceService.calculate_balance")
    def test_balance_returns_paginated_response(self, mock_calculate_balance):
        """Response should be paginated and include total_quantity."""
        mock_calculate_balance.return_value = {
            "sector": ElecOperation.SECTOR,
            "quantity": {"credit": 120.0, "debit": 30.0},
            "available_balance": 90.0,
            "pending_teneur": 10.0,
            "declared_teneur": 5.0,
            "pending_operations": 2,
            "emission_rate_per_mj": ElecOperation.EMISSION_RATE_PER_MJ,
        }
        request = self._make_request()

        response = self.view.balance(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertIn("total_quantity", response.data)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["total_quantity"], 90.0)
        self.assertEqual(response.data["results"][0]["available_balance"], 90.0)
        self.assertEqual(response.data["results"][0]["quantity"]["credit"], 120.0)
