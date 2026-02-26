from datetime import date, timedelta

from django.core.management.base import BaseCommand

from core.models import Entity
from tiruert.models.declaration_period import TiruertDeclarationPeriod
from tiruert.services.objective_snapshot import ObjectiveSnapshotService


class Command(BaseCommand):
    help = """
    Snapshot objectives for all Tiruert-liable entities the day after a declaration period closes.
    This command should be run every day (e.g., via cron).

    For each entity, it computes and persists an ObjectiveSnapshot for the closed period's year.
    Past years will then be served from these snapshots instead of being recomputed on every request.

    Usage:
        python web/manage.py snapshot_objectives
    """

    def handle(self, *args, **options):
        yesterday = date.today() - timedelta(days=1)
        period_closed_yesterday = TiruertDeclarationPeriod.objects.filter(end_date=yesterday).first()

        if not period_closed_yesterday:
            self.stdout.write(self.style.SUCCESS("No declaration period closed yesterday. No snapshots created."))
            return

        year = period_closed_yesterday.year

        self.stdout.write(f"Declaration period for year {year} closed on {yesterday}. Starting snapshot creation...")

        tiruert_liable_entities = Entity.objects.filter(is_tiruert_liable=True)
        if not tiruert_liable_entities.exists():
            self.stdout.write(self.style.WARNING("No Tiruert-liable entities found."))
            return

        created_count = 0
        skipped_count = 0

        for entity in tiruert_liable_entities:
            snapshot = ObjectiveSnapshotService.create_snapshot(
                entity_id=entity.id,
                year=year,
            )
            if snapshot is not None:
                created_count += 1
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"  Skipped entity {entity.id} ({entity.name}): no data available."))

        self.stdout.write(
            self.style.SUCCESS(f"Snapshot done for year {year}: {created_count} created/updated, {skipped_count} skipped.")
        )
