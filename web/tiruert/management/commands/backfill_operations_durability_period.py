from django.core.management.base import BaseCommand

from tiruert.models.operation import Operation
from tiruert.models.operation_detail import OperationDetail


class Command(BaseCommand):
    help = """
    For all MAC_BIO, INCORPORATION and LIVRAISON_DIRECTE operations that have no durability_period,
    set the durability_period from the first related operation detail's lot period.

    Usage:
        python web/manage.py backfill_operations_durability_period
    """

    def handle(self, *args, **options):
        operations = Operation.objects.filter(
            type__in=[Operation.MAC_BIO, Operation.INCORPORATION, Operation.LIVRAISON_DIRECTE],
            durability_period__isnull=True,
        )

        total = operations.count()
        self.stdout.write(f"Found {total} operations without durability_period.")

        updated = 0
        skipped = 0

        for operation in operations.iterator(chunk_size=1000):
            first_detail = OperationDetail.objects.filter(operation=operation).select_related("lot").first()

            if first_detail is None or first_detail.lot is None:
                self.stdout.write(self.style.WARNING(f"  Operation {operation.id}: no detail/lot found, skipping."))
                skipped += 1
                continue

            operation.durability_period = str(first_detail.lot.period)
            operation.save(update_fields=["durability_period"])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Done. {updated} operations updated, {skipped} skipped."))
