from collections import defaultdict
from functools import partial

from django.db.models import Prefetch, Q

from tiruert.models import Operation
from tiruert.models.operation_detail import OperationDetail
from tiruert.services.balance_annotations import calculate_balance_with_annotations
from tiruert.services.balance_filters import apply_operation_detail_filters
from tiruert.services.declaration_period import DeclarationPeriodService


class BalanceService:
    GROUP_BY_SECTOR = "sector"
    GROUP_BY_CATEGORY = "customs_category"
    GROUP_BY_LOT = "lot"

    @staticmethod
    def _get_key(operation, group_by, detail=None):
        """
        Build grouping key for non-annotated balance paths (lot).
        """
        # Base key for lot/depot grouping
        key = (operation.sector, operation.customs_category, operation.biofuel.code)

        # Add additional elements to the key based on the grouping type
        if group_by == BalanceService.GROUP_BY_LOT and detail:
            return key + (detail.lot.id,)

        return key

    @staticmethod
    def _init_balance_entry(unit="l"):
        """
        Initializes a balance entry with default values
        """
        entry = {
            "sector": None,
            "customs_category": None,
            "biofuel": None,
            "quantity": {"credit": 0, "debit": 0},
            "emission_rate_per_mj": 0,
            "pending_teneur": 0,
            "pending_operations": 0,
            "declared_teneur": 0,
            "available_balance": 0,
            "unit": unit,
            "ghg_reduction_min": None,
            "ghg_reduction_max": None,
            "saved_emissions": 0,
            "pending_saved_emissions": 0,
            "declared_saved_emissions": 0,
        }

        return entry

    @staticmethod
    def _init_lot_balance_entry(unit="l"):
        """
        Initializes a balance entry for lot grouping.
        This path does not expose teneur fields and uses volume directly.
        """
        entry = {
            "sector": None,
            "customs_category": None,
            "biofuel": None,
            "volume": {"credit": 0, "debit": 0},
            "emission_rate_per_mj": 0,
            "pending_operations": 0,
            "available_balance": 0,
            "unit": unit,
            "saved_emissions": 0,
        }

        return entry

    def _update_volume(balance, key, credit_operation, volume):
        """
        Updates lot volume credit/debit values.
        """
        volume_type = "credit" if credit_operation else "debit"
        balance[key]["volume"][volume_type] += volume

    @staticmethod
    def _update_available_balance(balance, key, operation, detail, credit_operation, volume):
        """
        Updates the balance entry with the details of the operation
        """
        volume_sign = 1 if credit_operation else -1
        balance[key]["available_balance"] += volume * volume_sign

        balance[key]["emission_rate_per_mj"] = detail.emission_rate_per_mj  # used when displaying balance by lot

        avoided_emissions = detail.avoided_emissions
        balance[key]["saved_emissions"] += avoided_emissions * volume_sign

    @staticmethod
    def resolve_lot_ids_for_durability_period(operations, durability_period):
        """
        Returns the list of lot_ids belonging to credit operations with the given durability_period.
        These lot_ids are then passed as a detail_filter so that all operations referencing
        those lots (including debits like TENEUR) are included in the balance calculation.
        """
        return list(
            operations.filter(durability_period__in=durability_period).values_list("details__lot_id", flat=True).distinct()
        )

    @staticmethod
    def _prefetch_filtered_details(operations, detail_filters=None):
        """
        Pre-filter OperationDetails at DB level using Prefetch.
        detail_filters keys: ges_bound_min, ges_bound_max, feedstock, origin_country, lot_ids
        """
        details_qs = OperationDetail.objects.select_related("lot")
        details_qs = apply_operation_detail_filters(details_qs, detail_filters)

        return operations.prefetch_related(Prefetch("details", queryset=details_qs, to_attr="prefetched_details"))

    @staticmethod
    def _filter_operations_for_current_year(operations):
        current_year = DeclarationPeriodService.get_current_declaration_year()
        if current_year is None:
            return operations

        return operations.filter(
            (Q(durability_period__isnull=True) | Q(durability_period__lt=str(current_year + 1)))
            & (Q(declaration_year__isnull=True) | Q(declaration_year__lte=current_year))
        )

    @staticmethod
    def _calculate_balance_for_lot(operations, entity_id, group_by, date_from=None, detail_filters=None):
        # Use a defaultdict with a factory function that creates an appropriate balance entry
        balance = defaultdict(partial(BalanceService._init_lot_balance_entry))

        operations = operations.filter(status__in=Operation.ACTIVE_STATUSES)

        operations = BalanceService._prefetch_filtered_details(operations, detail_filters)

        for operation in operations:
            credit_operation = operation.is_credit(entity_id)

            last_key = None

            for detail in operation.prefetched_details:
                key = BalanceService._get_key(operation, group_by, detail)
                last_key = key
                balance[key]["sector"] = operation.sector
                balance[key]["customs_category"] = operation.customs_category
                balance[key]["biofuel"] = operation.biofuel

                if not (credit_operation and operation.status in [Operation.PENDING, Operation.DRAFT]):
                    volume = detail.volume
                    BalanceService._update_available_balance(balance, key, operation, detail, credit_operation, volume)

                    if date_from is None or operation.created_at >= date_from:
                        BalanceService._update_volume(balance, key, credit_operation, volume)

            if last_key is not None and operation.status in [Operation.PENDING, Operation.DRAFT]:
                balance[last_key]["pending_operations"] += 1

        return balance

    @staticmethod
    def calculate_balance(operations, entity_id, group_by, unit, date_from=None, detail_filters=None):
        """
        Calculates balances based on the specified grouping
        'operations' is a queryset of already filtered operations

        Parameters:
        - operations: QuerySet of Operation objects to be included in the balance calculation
        - entity_id: ID of the entity for which the balance is being calculated
        - group_by: The grouping type for the balance calculation (e.g., sector, category, lot)
        - unit: The unit for the balance calculation
        - date_from: (Optional) used to calculate teneur on a specific period
        - detail_filters: (Optional) dict with lot-level filters (ges_bound_min, ges_bound_max, feedstock, origin_country)

        Returns:
        - A dictionary containing the calculated balances based on the specified grouping
        """
        operations = BalanceService._filter_operations_for_current_year(operations)
        operations = operations.exclude_informative()

        if group_by in [None, BalanceService.GROUP_BY_SECTOR, BalanceService.GROUP_BY_CATEGORY]:
            return calculate_balance_with_annotations(
                operations,
                entity_id,
                group_by,
                unit,
                date_from,
                detail_filters,
                init_entry=BalanceService._init_balance_entry,
            )

        return BalanceService._calculate_balance_for_lot(
            operations,
            entity_id,
            group_by,
            date_from,
            detail_filters,
        )
