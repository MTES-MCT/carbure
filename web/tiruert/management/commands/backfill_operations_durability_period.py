from django.core.management.base import BaseCommand
from django.db.models import OuterRef, Subquery

from tiruert.models.operation import Operation
from tiruert.models.operation_detail import OperationDetail

BATCH_SIZE = 1000


class Command(BaseCommand):
    help = """
    For all MAC_BIO, INCORPORATION and LIVRAISON_DIRECTE operations that have no durability_period,
    set the durability_period from the first related operation detail's lot period.

    Usage:
        python web/manage.py backfill_operations_durability_period --dry-run=false
        python web/manage.py backfill_operations_durability_period --dry-run=true
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            choices=["true", "false"],
            default="true",
            help="Simulate changes without saving to database",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run") == "true"

        first_detail_period = OperationDetail.objects.filter(operation=OuterRef("pk")).values("lot__period")[:1]

        operations = Operation.objects.filter(
            type__in=[Operation.MAC_BIO, Operation.INCORPORATION, Operation.LIVRAISON_DIRECTE],
            durability_period__isnull=True,
        ).annotate(lot_period=Subquery(first_detail_period))

        total = operations.count()
        self.stdout.write(f"Found {total} operations without durability_period.")

        updated = 0
        skipped = 0
        batch = []

        for operation in operations.iterator(chunk_size=BATCH_SIZE):
            if operation.lot_period is None:
                self.stdout.write(self.style.WARNING(f"  Operation {operation.id}: no detail/lot found, skipping."))
                skipped += 1
                continue

            operation.durability_period = str(operation.lot_period)
            batch.append(operation)
            updated += 1

            if len(batch) >= BATCH_SIZE:
                if not dry_run:
                    Operation.objects.bulk_update(batch, ["durability_period"])
                batch.clear()

        if batch and not dry_run:
            Operation.objects.bulk_update(batch, ["durability_period"])

        if dry_run:
            self.stdout.write(self.style.WARNING(f"Dry run. {updated} operations would be updated, {skipped} skipped."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Done. {updated} operations updated, {skipped} skipped."))
