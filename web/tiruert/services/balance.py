from collections import defaultdict
from functools import partial

from django.db.models import Prefetch

from tiruert.models import Operation
from tiruert.models.operation_detail import OperationDetail
from tiruert.services.balance_annotations import calculate_balance_with_annotations
from tiruert.services.balance_filters import apply_operation_detail_filters


class BalanceService:
    GROUP_BY_SECTOR = "sector"
    GROUP_BY_CATEGORY = "customs_category"
    GROUP_BY_LOT = "lot"
    GROUP_BY_DEPOT = "depot"
    UNIT_CONVERSION_RULES = {
        "mj": ("pci_litre", 1),
    }

    @staticmethod
    def _get_key(operation, group_by, detail=None, depot=None):
        """
        Build grouping key for non-annotated balance paths (lot/depot).
        """
        # Base key for lot/depot grouping
        key = (operation.sector, operation.customs_category, operation.biofuel.code)

        # Add additional elements to the key based on the grouping type
        if group_by == BalanceService.GROUP_BY_LOT and detail:
            return key + (detail.lot.id,)
        elif group_by == BalanceService.GROUP_BY_DEPOT and depot:
            return key + (depot,)

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

    def _update_quantity_and_teneur(balance, key, operation, detail, credit_operation, quantity):
        """
        Updates the balance entry with the details of the operation.
        For lot/depot grouping, quantity and teneur updates are applied on the same key.
        """
        if operation.type == Operation.TENEUR:
            teneur_type = "pending_teneur" if operation.status == Operation.PENDING else "declared_teneur"
            balance[key][teneur_type] += quantity

            avoided_type = "pending_saved_emissions" if operation.status == Operation.PENDING else "declared_saved_emissions"
            balance[key][avoided_type] += detail.avoided_emissions

        quantity_type = "credit" if credit_operation else "debit"
        balance[key]["quantity"][quantity_type] += quantity

    @staticmethod
    def _update_available_balance(balance, key, operation, detail, credit_operation, quantity):
        """
        Updates the balance entry with the details of the operation
        """
        volume_sign = 1 if credit_operation else -1
        balance[key]["available_balance"] += quantity * volume_sign

        balance[key]["emission_rate_per_mj"] = detail.emission_rate_per_mj  # used when displaying balance by lot

        avoided_emissions = detail.avoided_emissions
        balance[key]["saved_emissions"] += avoided_emissions * volume_sign

    @staticmethod
    def _calculate_quantity(operation, detail):
        return detail.volume * operation.renewable_energy_share

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
    def _calculate_balance_for_lot_or_depot(operations, entity_id, group_by, date_from=None, detail_filters=None):
        # Use a defaultdict with a factory function that creates an appropriate balance entry
        balance = defaultdict(partial(BalanceService._init_balance_entry))
        is_depot_grouping = group_by == BalanceService.GROUP_BY_DEPOT

        operations = operations.filter(status__in=Operation.ACTIVE_STATUSES)

        operations = BalanceService._prefetch_filtered_details(operations, detail_filters)

        for operation in operations:
            credit_operation = operation.is_credit(entity_id)

            depot = None
            if is_depot_grouping:
                depot = operation.to_depot if credit_operation else operation.from_depot
                if depot is None:
                    continue

            last_key = None

            for detail in operation.prefetched_details:
                key = BalanceService._get_key(operation, group_by, detail, depot)
                last_key = key
                balance[key]["sector"] = operation.sector
                balance[key]["customs_category"] = operation.customs_category
                balance[key]["biofuel"] = operation.biofuel

                if not (credit_operation and operation.status in [Operation.PENDING, Operation.DRAFT]):
                    quantity = BalanceService._calculate_quantity(operation, detail)
                    BalanceService._update_available_balance(balance, key, operation, detail, credit_operation, quantity)

                    if date_from is None or operation.created_at >= date_from:
                        BalanceService._update_quantity_and_teneur(
                            balance, key, operation, detail, credit_operation, quantity
                        )

            if last_key is not None and operation.status in [Operation.PENDING, Operation.DRAFT]:
                balance[last_key]["pending_operations"] += 1

        if is_depot_grouping:
            balance = BalanceService._update_depot_debit_with_teneur_and_transfert(entity_id, balance, operations)

        return balance

    @staticmethod
    def calculate_balance(operations, entity_id, group_by, unit, date_from=None, detail_filters=None):
        """
        Calculates balances based on the specified grouping
        'operations' is a queryset of already filtered operations

        Parameters:
        - operations: QuerySet of Operation objects to be included in the balance calculation
        - entity_id: ID of the entity for which the balance is being calculated
        - group_by: The grouping type for the balance calculation (e.g., sector, category, lot, depot)
        - unit: The unit for the balance calculation
        - date_from: (Optional) used to calculate teneur on a specific period
        - detail_filters: (Optional) dict with lot-level filters (ges_bound_min, ges_bound_max, feedstock, origin_country)

        Returns:
        - A dictionary containing the calculated balances based on the specified grouping
        """
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

        return BalanceService._calculate_balance_for_lot_or_depot(
            operations,
            entity_id,
            group_by,
            date_from,
            detail_filters,
        )

    @staticmethod
    def _update_depot_debit_with_teneur_and_transfert(entity_id, balance, operations):
        """
        Updates the balance by distributing teneur and transfert volumes across depots as debits
        """
        # Fetch all teneur and transfert operations
        teneurs = operations.filter(
            type__in=[
                Operation.TENEUR,
                Operation.TRANSFERT,
            ],
        ).prefetch_related("details__lot")

        # Collect all lot_ids from the teneur and transfert operations
        lot_ids = []
        for teneur in teneurs:
            for detail in teneur.details.all():
                lot_ids.append(detail.lot.id)

        # Group credited operations by lot_id
        credit_operations_with_lots = (
            Operation.objects.filter(
                credited_entity=entity_id,
                details__lot_id__in=lot_ids,
                status__in=[Operation.VALIDATED, Operation.ACCEPTED, Operation.CORRECTED],
            )
            .prefetch_related("details__lot")
            .order_by("details__lot_id", "-created_at")
        )

        # Create a mapping of lot_id to operations
        credited_operations = {}
        for operation in credit_operations_with_lots:
            # Case of TRANSFERT for instance
            if operation.to_depot is None:
                continue

            for detail in operation.details.all():
                if detail.lot_id in lot_ids:
                    if detail.lot_id not in credited_operations:
                        credited_operations[detail.lot_id] = []
                    credited_operations[detail.lot_id].append(
                        {
                            "operation": operation,
                            "depot": operation.to_depot,
                        }
                    )

        # Process each teneur/transfert operation and distribute its volume across depots
        for teneur in teneurs:
            for detail in teneur.details.all():
                remaining_volume = detail.volume  # Initialize volume to distribute between depots

                if detail.lot_id in credited_operations:
                    operations = credited_operations[detail.lot_id]

                    # Try to distribute the teneur volume across all available depots
                    for operation in operations:
                        if remaining_volume <= 0:
                            break

                        depot = operation["depot"]
                        key = (teneur.sector, teneur.customs_category, teneur.biofuel.code, depot)

                        # Calculate how much volume can be debited from this depot
                        credit = balance[key]["quantity"]["credit"]
                        current_debit = balance[key]["quantity"]["debit"]
                        available_credit = max(0, credit - current_debit)

                        # Determine the volume to debit from this depot
                        volume_to_debit = min(remaining_volume, available_credit)

                        if volume_to_debit > 0:
                            # Update the debit amount
                            balance[key]["quantity"]["debit"] += volume_to_debit
                            # Round to 2 decimals after each operation to prevent float precision errors accumulation
                            balance[key]["quantity"]["debit"] = round(balance[key]["quantity"]["debit"], 2)
                            remaining_volume -= volume_to_debit
                            # Round to 2 decimals after each operation to prevent float precision errors accumulation
                            remaining_volume = round(remaining_volume, 2)

        return balance
