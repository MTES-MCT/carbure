import logging
from datetime import datetime, time

from django.db.models import Q
from django.utils.timezone import make_aware

from tiruert.models import MacFossilFuel, Objective, ObjectiveSnapshot, Operation
from tiruert.models.elec_operation import ElecOperation
from tiruert.services.objective import ObjectiveService

logger = logging.getLogger(__name__)


class ObjectiveSnapshotService:
    @staticmethod
    def compute(entity_id, year):
        """
        Compute objectives for an entity/year without needing a ViewSet or request.
        Dates (date_from, date_to) are derived from the TiruertDeclarationPeriod for the given year.

        Args:
            entity_id: ID of the entity
            year: Declaration year (int)

        Returns:
            dict with keys 'main', 'sectors', 'categories', or None if data is missing.
        """
        from tiruert.services.declaration_period import DeclarationPeriodService

        period = DeclarationPeriodService.get_period_by_year(year)
        if period is None:
            logger.info("No declaration period found for year %s, skipping snapshot for entity %s.", year, entity_id)
            return None

        date_from = period.start_date
        date_to = make_aware(datetime.combine(period.end_date, time.max))
        # Objectives
        objectives = Objective.objects.filter(year=year)
        if not objectives.exists():
            logger.info("No objectives found for year %s, skipping snapshot for entity %s.", year, entity_id)
            return None

        # MacFossilFuel
        macs = MacFossilFuel.objects.filter(operator_id=entity_id, year=year)
        if not macs.exists():
            logger.info("No MacFossilFuel found for entity %s / year %s, skipping snapshot.", entity_id, year)
            return None

        # Operations (all history up to period end — balance is computed from all history)
        operations = Operation.objects.filter(
            Q(credited_entity=entity_id) | Q(debited_entity=entity_id),
            created_at__lte=date_to,
        ).distinct()

        if not operations.exists():
            logger.info("No operations found for entity %s up to %s, skipping snapshot.", entity_id, date_to)
            return None

        elec_ops = ElecOperation.objects.filter(
            Q(credited_entity=entity_id) | Q(debited_entity=entity_id),
            created_at__lte=date_to,
        ).distinct()

        return ObjectiveService.build_objectives_result(
            objectives, macs, operations, elec_ops, entity_id, date_from, year=year
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
            logger.info("No declaration period found for year %s, cannot create snapshot.", year)
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
        logger.info("%s objective snapshot for entity %s / year %s.", action, entity_id, year)
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
