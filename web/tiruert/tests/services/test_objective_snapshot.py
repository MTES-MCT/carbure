from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from core.models import Entity
from tiruert.models import ObjectiveSnapshot
from tiruert.services.objective_snapshot import ObjectiveSnapshotService


class CreateSnapshotBalanceTest(TestCase):
    def test_persists_balances_by_sector_biofuel_and_category(self):
        """Persist detailed balances in liters and MJ with a single calculation."""
        entity = Entity.objects.create(name="Operator", entity_type=Entity.OPERATOR)
        period = SimpleNamespace(start_date=date(2025, 1, 1), end_date=date(2026, 3, 31))
        key = ("ESSENCE", "EP2AM", "ETH")
        entry = {
            "sector": "ESSENCE",
            "customs_category": "EP2AM",
            "biofuel": SimpleNamespace(code="ETH"),
            "available_balance": 123,
            "energy_mj": 2500,
            "saved_emissions": 4.5,
        }

        with (
            patch("tiruert.services.declaration_period.DeclarationPeriodService.get_period_by_year", return_value=period),
            patch.object(ObjectiveSnapshotService, "compute", return_value={"main": {}}),
            patch(
                "tiruert.services.objective_snapshot.BalanceService.calculate_balance", return_value={key: entry}
            ) as calculate,
        ):
            snapshot = ObjectiveSnapshotService.create_snapshot(entity.id, 2025)

        self.assertEqual(
            snapshot.data_balance,
            [
                {
                    "sector": "ESSENCE",
                    "customs_category": "EP2AM",
                    "biofuel": "ETH",
                    "volume": 123,
                    "energy": 2500,
                    "saved_emissions": 4.5,
                }
            ],
        )
        self.assertEqual(ObjectiveSnapshot.objects.get(entity=entity, year=2025).data_balance, snapshot.data_balance)
        calculate.assert_called_once()
        self.assertEqual(calculate.call_args.args[2:4], (None, "l"))
        self.assertTrue(calculate.call_args.kwargs["include_energy"])

    def test_compute_balance_uses_one_detailed_aggregation(self):
        """Keep energy in MJ from one balance aggregation for the closed year."""
        entity = Entity.objects.create(name="Operator", entity_type=Entity.OPERATOR)
        entry = {
            "sector": "ESSENCE",
            "customs_category": "EP2AM",
            "biofuel": SimpleNamespace(code="ETH"),
            "available_balance": 123,
            "energy_mj": 2500,
            "saved_emissions": 4.5,
        }
        with patch(
            "tiruert.services.objective_snapshot.BalanceService.calculate_balance",
            return_value={("ESSENCE", "EP2AM", "ETH"): entry},
        ) as calculate:
            result = ObjectiveSnapshotService.compute_balance(entity.id, 2025, date(2026, 3, 31))

        self.assertEqual(
            result,
            [
                {
                    "sector": "ESSENCE",
                    "customs_category": "EP2AM",
                    "biofuel": "ETH",
                    "volume": 123,
                    "energy": 2500,
                    "saved_emissions": 4.5,
                }
            ],
        )
        calculate.assert_called_once()
        self.assertEqual(calculate.call_args.args[2:4], (None, "l"))
        self.assertEqual(calculate.call_args.kwargs, {"declaration_year": 2025, "include_energy": True})


class GetCachedAggregatedTest(TestCase):
    """Unit tests for ObjectiveSnapshotService.get_cached_aggregated()."""

    def setUp(self):
        cache.clear()

    def test_returns_none_on_cache_miss(self):
        """Returns None when no value is cached for the year."""
        result = ObjectiveSnapshotService.get_cached_aggregated(2025)
        self.assertIsNone(result)

    def test_returns_cached_value_on_cache_hit(self):
        """Returns the cached dict when one exists for the year."""
        expected = {"main": {"available_balance": 42}, "sectors": [], "categories": []}
        cache.set("tiruert:aggregated_objectives:2025", expected)

        result = ObjectiveSnapshotService.get_cached_aggregated(2025)

        self.assertEqual(result, expected)

    def test_different_years_are_independent(self):
        """Cache entries for different years do not interfere."""
        data_2024 = {"main": {"available_balance": 10}, "sectors": [], "categories": []}
        data_2025 = {"main": {"available_balance": 20}, "sectors": [], "categories": []}
        cache.set("tiruert:aggregated_objectives:2024", data_2024)
        cache.set("tiruert:aggregated_objectives:2025", data_2025)

        self.assertEqual(ObjectiveSnapshotService.get_cached_aggregated(2024), data_2024)
        self.assertEqual(ObjectiveSnapshotService.get_cached_aggregated(2025), data_2025)
        self.assertIsNone(ObjectiveSnapshotService.get_cached_aggregated(2026))


class ComputeAndCacheAggregatedTest(TestCase):
    """Unit tests for ObjectiveSnapshotService.compute_and_cache_aggregated()."""

    def setUp(self):
        cache.clear()

    def test_returns_none_when_no_tiruert_liable_entities(self):
        """Returns None and writes nothing to cache when no entity is tiruert-liable."""
        result = ObjectiveSnapshotService.compute_and_cache_aggregated(2025)

        self.assertIsNone(result)
        self.assertIsNone(cache.get("tiruert:aggregated_objectives:2025"))

    def test_returns_none_when_no_data_for_any_entity(self):
        """Returns None when all entities return no data (snapshot and compute both fail)."""
        Entity.objects.create(name="E1", entity_type=Entity.OPERATOR, is_tiruert_liable=True)

        with (
            patch.object(ObjectiveSnapshotService, "get_snapshot", return_value=None),
            patch.object(ObjectiveSnapshotService, "compute", return_value=None),
        ):
            result = ObjectiveSnapshotService.compute_and_cache_aggregated(2025)

        self.assertIsNone(result)
        self.assertIsNone(cache.get("tiruert:aggregated_objectives:2025"))

    def test_prefers_db_snapshot_over_live_compute(self):
        """Uses get_snapshot() result when available; does not call compute()."""
        entity = Entity.objects.create(name="E1", entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        snapshot_data = {"main": {"available_balance": 50}, "sectors": [], "categories": []}
        aggregated = {"main": {"available_balance": 50}, "sectors": [], "categories": []}

        with (
            patch.object(ObjectiveSnapshotService, "get_snapshot", return_value=snapshot_data) as mock_snap,
            patch.object(ObjectiveSnapshotService, "compute") as mock_compute,
            patch("tiruert.services.objective_snapshot.ObjectiveService.aggregate_objectives", return_value=aggregated),
        ):
            result = ObjectiveSnapshotService.compute_and_cache_aggregated(2025)
            mock_snap.assert_called_once_with(entity.id, 2025)
            mock_compute.assert_not_called()

        self.assertEqual(result, aggregated)

    def test_falls_back_to_live_compute_when_no_snapshot(self):
        """Falls back to compute() when get_snapshot() returns None."""
        entity = Entity.objects.create(name="E1", entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        computed_data = {"main": {"available_balance": 100}, "sectors": [], "categories": []}
        aggregated = {"main": {"available_balance": 100}, "sectors": [], "categories": []}

        with (
            patch.object(ObjectiveSnapshotService, "get_snapshot", return_value=None),
            patch.object(ObjectiveSnapshotService, "compute", return_value=computed_data) as mock_compute,
            patch("tiruert.services.objective_snapshot.ObjectiveService.aggregate_objectives", return_value=aggregated),
        ):
            result = ObjectiveSnapshotService.compute_and_cache_aggregated(2025)
            mock_compute.assert_called_once_with(entity.id, 2025)

        self.assertEqual(result, aggregated)
