from itertools import zip_longest

from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from core.models import Entity
from core.models.declaration_period import SustainabilityDeclaration
from core.models.lot import CarbureLot
from tiruert.models.operation import Operation
from tiruert.services.operation import OperationService


class Command(BaseCommand):
    help = """
    For all entities ("is_tiruert_liable=True"), create TiruertOperation records for all past durability periods,
    for a specific year, if they don't already exist.

    Usage:
        python web/manage.py backfill_operations_for_past_periods --year=2025
    """

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, help="Year for which to initialize past periods operations", required=True)

    def handle(self, *args, **options):
        year = options.get("year")

        entities = Entity.objects.filter(is_tiruert_liable=True, is_enabled=True, closed_at__isnull=True)
        for entity in entities:
            self.stdout.write(f"Initializing operations for entity {entity.id} - {entity.name}...")
            self.init_operations_for_past_periods(year, entity.id)
            self.stdout.write(f"Finished initializing operations for entity {entity.id} - {entity.name}", ending="\n\n")

    def init_operations_for_past_periods(self, year, entity_id):
        declaration_lots = (
            CarbureLot.objects.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
            .filter(year=year)
            .filter(Q(carbure_supplier_id=entity_id) | Q(carbure_client_id=entity_id))
        )

        sent_lots = declaration_lots.filter(carbure_supplier_id=entity_id)
        received_lots = declaration_lots.filter(carbure_client_id=entity_id)

        mac_lots = sent_lots.filter(delivery_type=CarbureLot.RFC, carbure_supplier__has_mac=True)
        tiruert_lots = received_lots | mac_lots

        periods = tiruert_lots.values_list("period", flat=True).distinct()
        operations_counting_before = list(self.count_operations_per_period(entity_id, year))

        for period in periods:
            lots = tiruert_lots.filter(period=period)

            declaration_period_str = f"{str(period)[:4]}-{str(period)[4:6]}-01"
            try:
                SustainabilityDeclaration.objects.get(
                    period=declaration_period_str,
                    entity_id=entity_id,
                    declared=True,
                )
            except SustainabilityDeclaration.DoesNotExist:
                continue  # skip if no declaration exists for this period and entity

            pending_lots = lots.filter(lot_status=CarbureLot.PENDING)
            if pending_lots.exists():
                continue

            in_correction_lots = lots.filter(correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED])
            if in_correction_lots.exists():
                continue

            rejected_lots = lots.filter(lot_status=CarbureLot.REJECTED)
            if rejected_lots.exists():
                continue

            OperationService.create_operations_from_lots(lots)

        operations_counting_after = list(self.count_operations_per_period(entity_id, year))
        self.display_operations_count(operations_counting_before, operations_counting_after)

    def count_operations_per_period(self, entity_id, year):
        return (
            Operation.objects.filter(
                credited_entity_id=entity_id,
                type__in=[Operation.MAC_BIO, Operation.INCORPORATION, Operation.LIVRAISON_DIRECTE],
                durability_period__startswith=year,
            )
            .values("durability_period")
            .annotate(count=Count("id"))
            .order_by("durability_period")
        )

    def display_operations_count(self, operations_counting_before, operations_counting_after):
        for period_before, period_after in zip_longest(operations_counting_before, operations_counting_after):
            before = period_before["count"] if period_before else 0
            after = period_after["count"] if period_after else 0
            result = after - before
            if result > 0 and period_after:
                self.stdout.write(
                    self.style.SUCCESS(f"  Period {period_after['durability_period']}: {result} operations created")
                )
