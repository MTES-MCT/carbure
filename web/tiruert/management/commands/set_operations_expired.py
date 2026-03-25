from collections import defaultdict
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db.models import F, Sum

from tiruert.models.declaration_period import TiruertDeclarationPeriod
from tiruert.models.operation import Operation
from tiruert.models.operation_detail import OperationDetail


class Command(BaseCommand):
    help = """
    Create EXPIRATION operations to zero out unused volumes from expired durability periods.
    Only the remaining (unused) volume of each lot is expired, preserving volumes already
    consumed by TENEUR, EXPORTATION, CESSION, etc.

    This command should be run every day.

    Usage:
        python web/manage.py set_operations_expired
    """

    def handle(self, *args, **options):
        yesterday = date.today() - timedelta(days=1)
        period_closed_yesterday = TiruertDeclarationPeriod.objects.filter(end_date=yesterday).first()

        if not period_closed_yesterday:
            self.stdout.write(self.style.SUCCESS("No declaration period closed yesterday. No operations updated."))
            return

        period = period_closed_yesterday.year - 1
        self.stdout.write(f"Processing expiration for durability period {period}...")

        # Skip if EXPIRATION operations already exist for this period
        existing_expirations = Operation.objects.filter(
            type=Operation.EXPIRATION,
            durability_period__startswith=str(period),
        ).exists()

        if existing_expirations:
            self.stdout.write(self.style.WARNING(f"EXPIRATION operations already exist for period {period}. Skipping."))
            return

        # Step 1: Find all lot_ids from expired period credit operations
        expired_lot_ids = list(
            OperationDetail.objects.filter(
                operation__type__in=Operation.CREDIT_TYPES,
                operation__durability_period__startswith=str(period),
                operation__status__in=Operation.CONFIRMED_STATUSES,
            )
            .values_list("lot_id", flat=True)
            .distinct()
        )

        if not expired_lot_ids:
            self.stdout.write(self.style.SUCCESS(f"No active confirmed operations found for period {period}."))
            return

        # Step 2: Cancel all PENDING or DRAFT operations linked to expired_lot_ids
        operation_ids_to_cancel = list(
            OperationDetail.objects.filter(
                lot_id__in=expired_lot_ids,
                operation__status__in=[Operation.PENDING, Operation.DRAFT],
            ).values_list("operation_id", flat=True)
        )
        if operation_ids_to_cancel:
            Operation.objects.filter(id__in=operation_ids_to_cancel).update(status=Operation.CANCELED)

        # Step 3: Find all entities that have credits on these lots
        entity_ids = list(
            OperationDetail.objects.filter(
                lot_id__in=expired_lot_ids,
                operation__credited_entity__isnull=False,
                operation__status__in=Operation.CONFIRMED_STATUSES,
            )
            .values_list("operation__credited_entity_id", flat=True)
            .distinct()
        )

        total_operations_created = 0
        total_details_created = 0

        # Step 4: For each entity, compute remaining volume per lot and create EXPIRATION operations
        for entity_id in entity_ids:
            operations_created, details_created = self._process_entity(entity_id, expired_lot_ids, period)
            total_operations_created += operations_created
            total_details_created += details_created

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total_operations_created} EXPIRATION operations "
                f"with {total_details_created} details for period {period}."
            )
        )

    def _process_entity(self, entity_id, expired_lot_ids, period):
        """
        For a given entity, compute remaining available volume per lot,
        then create EXPIRATION operations grouped by (biofuel, customs_category).
        """
        credit_map = self._get_credit_volumes(entity_id, expired_lot_ids)
        debit_map = self._get_debit_volumes(entity_id, expired_lot_ids)
        lots_to_expire = self._compute_remaining_volumes(credit_map, debit_map)

        if not lots_to_expire:
            return 0, 0

        lot_source_info = self._get_lot_source_info(lots_to_expire, entity_id, period)
        groups = self._group_lots_by_biofuel_and_category(lots_to_expire, lot_source_info)
        return self._create_expiration_operations(groups, lot_source_info, period)

    def _get_credit_volumes(self, entity_id, lot_ids):
        """Compute effective credit volumes per lot for an entity (volume * renewable_energy_share)."""
        credit_qs = (
            OperationDetail.objects.filter(
                lot_id__in=lot_ids,
                operation__credited_entity_id=entity_id,
                operation__status__in=Operation.CONFIRMED_STATUSES,
            )
            .values("lot_id")
            .annotate(total=Sum(F("volume") * F("operation__renewable_energy_share")))
        )
        return {row["lot_id"]: row["total"] or 0 for row in credit_qs}

    def _get_debit_volumes(self, entity_id, lot_ids):
        """Compute effective debit volumes per lot for an entity (volume * renewable_energy_share)."""
        debit_qs = (
            OperationDetail.objects.filter(
                lot_id__in=lot_ids,
                operation__debited_entity_id=entity_id,
                operation__status__in=Operation.ACTIVE_STATUSES,
            )
            .values("lot_id")
            .annotate(total=Sum(F("volume") * F("operation__renewable_energy_share")))
        )
        return {row["lot_id"]: row["total"] or 0 for row in debit_qs}

    @staticmethod
    def _compute_remaining_volumes(credit_map, debit_map):
        """Return a dict of {lot_id: remaining_volume} for lots with positive remaining volume."""
        lots_to_expire = {}
        for lot_id in credit_map:
            remaining = round(credit_map.get(lot_id, 0) - debit_map.get(lot_id, 0), 2)
            if remaining > 0:
                lots_to_expire[lot_id] = remaining
        return lots_to_expire

    @staticmethod
    def _get_lot_source_info(lots_to_expire, entity_id, period):
        """Fetch source operation metadata (biofuel, category, emission rate) for each lot.

        Uses any confirmed credit operation for this entity (INCORPORATION, CESSION, etc.)
        since the entity may have received its credit via CESSION, not just via CREDIT_TYPES.
        """
        source_details = OperationDetail.objects.filter(
            lot_id__in=list(lots_to_expire.keys()),
            operation__credited_entity_id=entity_id,
            operation__status__in=Operation.CONFIRMED_STATUSES,
        )

        lot_source_info = {}
        for detail in source_details:
            if detail.lot_id not in lot_source_info:
                lot_source_info[detail.lot_id] = {
                    "biofuel": detail.operation.biofuel,
                    "customs_category": detail.operation.customs_category,
                    "emission_rate_per_mj": detail.emission_rate_per_mj,
                    "entity": detail.operation.credited_entity,
                }
        return lot_source_info

    @staticmethod
    def _group_lots_by_biofuel_and_category(lots_to_expire, lot_source_info):
        """Group expirable lots by (biofuel_id, customs_category) to create one EXPIRATION per group."""
        groups = defaultdict(list)
        for lot_id, remaining_volume in lots_to_expire.items():
            if lot_id not in lot_source_info:
                continue
            info = lot_source_info[lot_id]
            group_key = (info["biofuel"].id, info["customs_category"])
            groups[group_key].append(
                {
                    "lot_id": lot_id,
                    "volume": remaining_volume,
                    "emission_rate_per_mj": info["emission_rate_per_mj"],
                }
            )
        return groups

    @staticmethod
    def _create_expiration_operations(groups, lot_source_info, period):
        """Create EXPIRATION operations with their details for each group."""
        operations_created = 0
        details_created = 0

        for (_biofuel_id, customs_category), lot_entries in groups.items():
            first_lot_info = lot_source_info[lot_entries[0]["lot_id"]]

            operation = Operation.objects.create(
                type=Operation.EXPIRATION,
                status=Operation.ACCEPTED,
                customs_category=customs_category,
                biofuel=first_lot_info["biofuel"],
                credited_entity=None,
                debited_entity=first_lot_info["entity"],
                from_depot=None,
                to_depot=None,
                renewable_energy_share=1,  # Volume already accounts for RES from source operations
                durability_period=str(period),
            )

            details_bulk = [
                OperationDetail(
                    operation=operation,
                    lot_id=entry["lot_id"],
                    volume=entry["volume"],
                    emission_rate_per_mj=entry["emission_rate_per_mj"],
                )
                for entry in lot_entries
            ]

            OperationDetail.objects.bulk_create(details_bulk)
            operations_created += 1
            details_created += len(details_bulk)

        return operations_created, details_created
