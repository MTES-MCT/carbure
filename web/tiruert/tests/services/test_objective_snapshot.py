from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from core.models import Entity
from tiruert.services.objective_snapshot import ObjectiveSnapshotService


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
