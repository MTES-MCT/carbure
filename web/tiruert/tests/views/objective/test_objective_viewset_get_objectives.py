from datetime import date
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Entity
from core.tests_utils import setup_current_user
from tiruert.models import ObjectiveSnapshot
from tiruert.services.objective_snapshot import ObjectiveSnapshotService

OBJECTIVES_URL = reverse("get-objectives")
SNAPSHOT_BALANCE_URL = reverse("get-snapshot-balance")

# Minimal valid payload that ObjectiveOutputSerializer can serialize
VALID_CACHED_OBJECTIVES = {
    "main": {
        "available_balance": 1000.0,
        "target": 500.0,
        "pending_teneur": 200.0,
        "declared_teneur": 100.0,
        "unit": "tCO2",
        "penalty": 0,
        "target_percent": 0.05,
        "energy_basis": 10000.0,
    },
    "sectors": [],
    "categories": [],
}


class ObjectiveViewSetAdminAggregatedTest(TestCase):
    """Integration tests for the admin aggregated objectives path (_get_aggregated_objectives)."""

    @classmethod
    def setUpTestData(cls):
        cls.admin_entity = Entity.objects.create(name="Admin Entity", entity_type=Entity.ADMIN)

    def setUp(self):
        cache.clear()
        setup_current_user(self, "admin@carbure.local", "Admin", "password", [(self.admin_entity, "ADMIN")], is_staff=True)

    def test_returns_503_when_cache_miss(self):
        """Admin without selected_entity_id gets 503 when no aggregated data is cached."""
        with self.assertLogs("django.request", level="ERROR"):
            response = self.client.get(
                OBJECTIVES_URL,
                {"entity_id": self.admin_entity.id, "year": 2025},
            )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_returns_200_with_cached_data(self):
        """Admin without selected_entity_id gets 200 with cached aggregated objectives."""
        cache.set("tiruert:aggregated_objectives:2025", VALID_CACHED_OBJECTIVES)

        response = self.client.get(
            OBJECTIVES_URL,
            {"entity_id": self.admin_entity.id, "year": 2025},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["main"]["available_balance"], 1000.0)

    def test_cache_is_read_with_correct_year_key(self):
        """Objectives are fetched from the cache key matching the requested year."""
        cache.set("tiruert:aggregated_objectives:2024", VALID_CACHED_OBJECTIVES)

        # Year 2025 has no cache → 503
        with self.assertLogs("django.request", level="ERROR"):
            response_2025 = self.client.get(
                OBJECTIVES_URL,
                {"entity_id": self.admin_entity.id, "year": 2025},
            )
        self.assertEqual(response_2025.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

        # Year 2024 is cached → 200
        response_2024 = self.client.get(
            OBJECTIVES_URL,
            {"entity_id": self.admin_entity.id, "year": 2024},
        )
        self.assertEqual(response_2024.status_code, status.HTTP_200_OK)

    def test_admin_reads_selected_entity_balance_only(self):
        """Admins can read a selected entity's snapshot but not an aggregated balance."""
        operator = Entity.objects.create(name="Operator", entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        ObjectiveSnapshot.objects.create(
            entity=operator,
            year=2025,
            date_from=date(2025, 1, 1),
            date_to=date(2026, 3, 31),
            data={},
            data_balance=[
                {
                    "sector": "ESSENCE",
                    "biofuel": "ETH",
                    "customs_category": "EP2AM",
                    "volume": 1,
                    "energy": 2,
                    "saved_emissions": 3,
                }
            ],
        )
        response = self.client.get(
            SNAPSHOT_BALANCE_URL,
            {
                "entity_id": self.admin_entity.id,
                "year": 2025,
                "selected_entity_id": operator.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["year"], 2025)
        self.assertEqual(response.data["results"][0]["biofuel"], "ETH")

        response = self.client.get(SNAPSHOT_BALANCE_URL, {"entity_id": self.admin_entity.id, "year": 2025})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ObjectiveViewSetOperatorTest(TestCase):
    """Integration tests verifying operators do not go through the admin aggregated path."""

    @classmethod
    def setUpTestData(cls):
        cls.operator_entity = Entity.objects.create(
            name="Operator",
            entity_type=Entity.OPERATOR,
            is_tiruert_liable=True,
            accise_number="ACC001",
        )

    def setUp(self):
        cache.clear()
        setup_current_user(self, "op@carbure.local", "Op", "password", [(self.operator_entity, "RW")])

    def test_operator_does_not_use_aggregated_cache(self):
        """Operator always goes through per-entity path; aggregated cache is never consulted."""
        with patch.object(ObjectiveSnapshotService, "get_cached_aggregated") as mock_cache:
            with patch(
                "tiruert.views.objective.objective.ObjectiveViewSet._get_objectives",
                return_value=None,
            ):
                self.client.get(
                    OBJECTIVES_URL,
                    {"entity_id": self.operator_entity.id, "year": 2025},
                )
                mock_cache.assert_not_called()

    def test_operator_reads_only_own_snapshot_balance(self):
        """Ignore a selected entity ID when an operator requests snapshot balances."""
        other = Entity.objects.create(name="Other", entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        ObjectiveSnapshot.objects.create(
            entity=other,
            year=2025,
            date_from=date(2025, 1, 1),
            date_to=date(2026, 3, 31),
            data={},
            data_balance=[
                {
                    "sector": "ESSENCE",
                    "biofuel": "ETH",
                    "customs_category": "EP2AM",
                    "volume": 1,
                    "energy": 2,
                    "saved_emissions": 3,
                }
            ],
        )
        response = self.client.get(
            SNAPSHOT_BALANCE_URL,
            {
                "entity_id": self.operator_entity.id,
                "year": 2025,
                "selected_entity_id": other.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_operator_reads_frozen_balance(self):
        """Return the operator's stored balance for the requested year."""
        ObjectiveSnapshot.objects.create(
            entity=self.operator_entity,
            year=2025,
            date_from=date(2025, 1, 1),
            date_to=date(2026, 3, 31),
            data={},
            data_balance=[
                {
                    "sector": "ESSENCE",
                    "biofuel": "ETH",
                    "customs_category": "EP2AM",
                    "volume": 1,
                    "energy": 2,
                    "saved_emissions": 3,
                }
            ],
        )
        response = self.client.get(SNAPSHOT_BALANCE_URL, {"entity_id": self.operator_entity.id, "year": 2025})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["energy"], 2)
