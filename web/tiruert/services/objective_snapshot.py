from datetime import datetime, time

from django.core.cache import cache
from django.db.models import Q
from django.utils.timezone import make_aware

from adapters.logger import log_info, log_warning
from tiruert.models import MacFossilFuel, Objective, ObjectiveSnapshot, Operation
from tiruert.models.elec_operation import ElecOperation
from tiruert.services.objective import ObjectiveService


class ObjectiveSnapshotService:
    @staticmethod
    def compute(entity_id, year):
        """
        Compute objectives for an entity/year without needing a ViewSet or request.
        Dates are derived from the TiruertDeclarationPeriod for the given year.

        Args:
            entity_id: ID of the entity
            year: Declaration year (int)

        Returns:
            dict with keys 'main', 'sectors', 'categories', or None if data is missing.
        """
        from tiruert.services.declaration_period import DeclarationPeriodService

        period = DeclarationPeriodService.get_period_by_year(year)
        if period is None:
            log_info(f"No declaration period found for year {year}, skipping snapshot for entity {entity_id}.")
            return None

        period_start = period.start_date
        date_to = make_aware(datetime.combine(period.end_date, time.max))
        # Objectives
        objectives = Objective.objects.filter(year=year)
        if not objectives.exists():
            log_info(f"No objectives found for year {year}, skipping snapshot for entity {entity_id}.")
            return None

        # MacFossilFuel
        macs = MacFossilFuel.objects.filter(operator_id=entity_id, year=year)
        if not macs.exists():
            log_info(f"No MacFossilFuel found for entity {entity_id} / year {year}, skipping snapshot.")
            return None

        # Operations (all history up to period end — balance is computed from all history)
        operations = Operation.objects.filter(
            Q(credited_entity=entity_id) | Q(debited_entity=entity_id),
            created_at__lte=date_to,
        ).distinct()

        if not operations.exists():
            log_info(f"No operations found for entity {entity_id} up to {date_to}, skipping snapshot.")
            return None

        elec_ops = ElecOperation.objects.filter(
            Q(credited_entity=entity_id) | Q(debited_entity=entity_id),
            created_at__lte=date_to,
        ).distinct()

        return ObjectiveService.build_objectives_result(
            objectives, macs, operations, elec_ops, entity_id, period_start, year=year
        )

    @staticmethod
    def create_snapshot(entity_id, year):
        """
        Compute and persist a snapshot for a given entity + year.
        Dates are derived from the TiruertDeclarationPeriod for the given year.
        Idempotent: updates the existing snapshot if one already exists.

        Args:
            entity_id: ID of the entity
            year: Declaration year (int)

        Returns:
            ObjectiveSnapshot instance, or None if computation yielded no data.
        """
        from tiruert.services.declaration_period import DeclarationPeriodService

        period = DeclarationPeriodService.get_period_by_year(year)
        if period is None:
            log_info(f"No declaration period found for year {year}, cannot create snapshot.")
            return None

        data = ObjectiveSnapshotService.compute(entity_id, year)
        if data is None:
            return None

        snapshot, created = ObjectiveSnapshot.objects.update_or_create(
            entity_id=entity_id,
            year=year,
            defaults={"data": data, "date_from": period.start_date, "date_to": period.end_date},
        )
        action = "Created" if created else "Updated"
        log_info(f"{action} objective snapshot for entity {entity_id} / year {year}.")
        return snapshot

    @staticmethod
    def get_snapshot(entity_id, year):
        """
        Return the snapshot data dict for a given entity + year, or None if not found.
        """
        try:
            snapshot = ObjectiveSnapshot.objects.get(entity_id=entity_id, year=year)
            return snapshot.data
        except ObjectiveSnapshot.DoesNotExist:
            return None

    # ------------------------------------------------------------------
    # Aggregated objectives cache (all tiruert-liable entities combined)
    # ------------------------------------------------------------------

    _AGGREGATED_CACHE_KEY = "tiruert:aggregated_objectives:{year}"
    _AGGREGATED_CACHE_TIMEOUT = 60 * 60 * 36  # 36 hours, data should be generated every 24h by a periodic task

    @staticmethod
    def get_cached_aggregated(year: int):
        """Return cached aggregated objectives for a given year, or None on cache miss."""
        return cache.get(ObjectiveSnapshotService._AGGREGATED_CACHE_KEY.format(year=year))

    @staticmethod
    def compute_and_cache_aggregated(year: int):
        """
        Compute aggregated objectives for all tiruert-liable entities for a given year
        and store the result in the Django cache.

        For each entity:
        - Uses the DB snapshot if one exists (past declaration years).
        - Falls back to a fresh computation otherwise (current year).

        Args:
            year: Declaration year (int)

        Returns:
            Aggregated objectives dict, or None if no data is available.
        """
        from core.models import Entity

        tiruert_liable_entities = Entity.objects.filter(is_tiruert_liable=True)
        if not tiruert_liable_entities.exists():
            log_warning(f"compute_and_cache_aggregated: no tiruert-liable entities found for year {year}.")
            return None

        objectives_list = []
        for entity in tiruert_liable_entities:
            # Prefer the persisted snapshot (fast DB read), fall back to live computation
            data = ObjectiveSnapshotService.get_snapshot(entity.id, year)
            if data is None:
                data = ObjectiveSnapshotService.compute(entity.id, year)
            if data:
                objectives_list.append(data)

        if not objectives_list:
            log_warning(f"compute_and_cache_aggregated: no data collected for year {year}.")
            return None

        result = ObjectiveService.aggregate_objectives(objectives_list)
        cache_key = ObjectiveSnapshotService._AGGREGATED_CACHE_KEY.format(year=year)
        cache.set(cache_key, result, ObjectiveSnapshotService._AGGREGATED_CACHE_TIMEOUT)
        log_info(f"Cached aggregated objectives for year {year} ({len(objectives_list)} entities).")
        return result
