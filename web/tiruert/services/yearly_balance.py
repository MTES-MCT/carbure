from django.db import transaction
from django.db.models import Q

from core.utils import truncate
from tiruert.models.operation import Operation
from tiruert.services.balance import BalanceService
from tiruert.services.operation import OperationService


class YearlyBalanceService:
    """
    Snapshot the remaining balance of every entity when a declaration year is closed.

    One YEARLY_BALANCE operation is created per balance line (biofuel / customs_category),
    carrying the snapshotted volume in a single lot-less OperationDetail.
    These operations are purely informative: they are excluded from every computation
    and export (see Operation.BALANCE_EXCLUDED_TYPES).
    """

    @staticmethod
    def snapshot_exists(year):
        return Operation.objects.filter(type=Operation.YEARLY_BALANCE, declaration_year=year).exists()

    @staticmethod
    def get_entity_ids(declaration_end_date):
        """Return ids of entities with confirmed credit operations up to declaration end date."""
        return list(
            Operation.objects.filter(
                credited_entity__isnull=False,
                status__in=Operation.CONFIRMED_STATUSES,
                created_at__date__lte=declaration_end_date,
            )
            .values_list("credited_entity_id", flat=True)
            .distinct()
        )

    @staticmethod
    @transaction.atomic
    def create_snapshot(year, declaration_end_date):
        """Create the YEARLY_BALANCE operations of the given declaration year for all entities."""
        operations_created = 0

        for entity_id in YearlyBalanceService.get_entity_ids(declaration_end_date):
            operations_created += YearlyBalanceService.create_snapshot_for_entity(entity_id, year, declaration_end_date)

        return operations_created

    @staticmethod
    def create_snapshot_for_entity(entity_id, year, declaration_end_date):
        operations = Operation.objects.filter(
            Q(credited_entity_id=entity_id) | Q(debited_entity_id=entity_id),
            created_at__date__lte=declaration_end_date,
        )
        balance = BalanceService.calculate_balance(operations, entity_id, None, "l")

        operations_created = 0

        for entry in balance.values():
            volume = truncate(entry["available_balance"])

            if volume < 0 or entry["biofuel"] is None:
                continue

            operation_data = {
                "type": Operation.YEARLY_BALANCE,
                "status": Operation.AUTO,
                "customs_category": entry["customs_category"],
                "biofuel": entry["biofuel"],
                "credited_entity_id": entity_id,
                "debited_entity": None,
                "declaration_year": year,
            }
            details_data = [
                {
                    "lot_id": None,
                    "volume": volume,
                    "emission_rate_per_mj": 0,
                    "avoided_emissions_tco2": entry["saved_emissions"],
                }
            ]
            OperationService.create_operation_with_details(operation_data, details_data)
            operations_created += 1

        return operations_created
