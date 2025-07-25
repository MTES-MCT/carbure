from collections import defaultdict
from functools import partial

from tiruert.models import Operation


class BalanceService:
    GROUP_BY_SECTOR = "sector"
    GROUP_BY_CATEGORY = "customs_category"
    GROUP_BY_LOT = "lot"
    GROUP_BY_DEPOT = "depot"
    GROUP_BY_ALL = [GROUP_BY_SECTOR, GROUP_BY_CATEGORY, GROUP_BY_LOT, GROUP_BY_DEPOT]

    @staticmethod
    def _get_key(operation, group_by, detail=None, depot=None):
        """
        Determines the appropriate key based on the grouping type
        """
        if group_by == BalanceService.GROUP_BY_SECTOR:
            return operation.sector
        elif group_by == BalanceService.GROUP_BY_CATEGORY:
            return operation.customs_category

        # Base key for other types of grouping
        key = (operation.sector, operation.customs_category, operation.biofuel.code)

        # Add additional elements to the key based on the grouping type
        if group_by == BalanceService.GROUP_BY_LOT and detail:
            return key + (detail.lot.id,)
        elif group_by == BalanceService.GROUP_BY_DEPOT and depot:
            return key + (depot,)

        return key

    @staticmethod
    def _get_conversion_factor(operation, unit):
        """
        Calculates the conversion factor based on the requested unit
        """
        conversion_factor_name = BalanceService._define_conversion_factor(unit)
        return getattr(operation.biofuel, conversion_factor_name, 1) if conversion_factor_name else 1

    @staticmethod
    def _define_conversion_factor(unit):
        """
        Determines the conversion factor based on the unit
        """
        conversion_factors = {"mj": "pci_litre", "kg": "masse_volumique"}
        return conversion_factors.get(unit)

    @staticmethod
    def _init_balance_entry(unit, operation=None, group_by=None):
        """
        Initializes a balance entry with default values
        """
        entry = {
            "sector": None if not operation else operation.sector,
            "customs_category": None if not operation else operation.customs_category,
            "biofuel": None if not operation else operation.biofuel,
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
        }

        return entry

    def _update_quantity_and_teneur(balance, key, operation, detail, credit_operation, conversion_factor):
        """
        Updates the balance entry with the details of the operation
        """
        quantity = detail.volume * conversion_factor * operation.renewable_energy_share

        if operation.type == Operation.TENEUR:
            teneur_type = "pending_teneur" if operation.status == Operation.PENDING else "declared_teneur"
            balance[key][teneur_type] += quantity

        quantity_type = "credit" if credit_operation else "debit"
        balance[key]["quantity"][quantity_type] += quantity

        return balance

    @staticmethod
    def _update_available_balance(balance, key, operation, detail, credit_operation, conversion_factor):
        """
        Updates the balance entry with the details of the operation
        """
        from tiruert.services.teneur import TeneurService

        volume_sign = 1 if credit_operation else -1
        quantity = detail.volume * conversion_factor * operation.renewable_energy_share
        balance[key]["available_balance"] += quantity * volume_sign
        balance[key]["emission_rate_per_mj"] = detail.emission_rate_per_mj  # used when displaying balance by lot

        avoided_emissions = TeneurService.convert_producted_emissions_to_avoided_emissions(
            detail.volume, operation.biofuel, detail.emission_rate_per_mj
        )
        balance[key]["saved_emissions"] += avoided_emissions * volume_sign
        return

    @staticmethod
    def _update_ghg_min_max(balance, key, detail):
        """
        Updates the GHG min and max values in the balance entry
        """
        balance[key]["ghg_reduction_min"] = min(
            filter(None, [balance[key].get("ghg_reduction_min"), detail.lot.ghg_reduction_red_ii])
        )

        balance[key]["ghg_reduction_max"] = max(
            filter(None, [balance[key].get("ghg_reduction_max"), detail.lot.ghg_reduction_red_ii])
        )
        return

    @staticmethod
    def calculate_balance(operations, entity_id, group_by, unit, date_from=None, ges_bound_min=None, ges_bound_max=None):
        """
        Calculates balances based on the specified grouping
        'operations' is a queryset of already filtered operations
        """
        # Use a defaultdict with a factory function that creates an appropriate balance entry
        balance = defaultdict(partial(BalanceService._init_balance_entry, unit))

        operations = operations.filter(
            status__in=[Operation.PENDING, Operation.ACCEPTED, Operation.VALIDATED, Operation.DECLARED]
        )

        for operation in operations:
            credit_operation = operation.is_credit(entity_id)

            depot = None
            if group_by == BalanceService.GROUP_BY_DEPOT:
                depot = operation.to_depot if credit_operation else operation.from_depot
                if depot is None:
                    continue

            conversion_factor = BalanceService._get_conversion_factor(operation, unit)

            for detail in operation.details.all():
                # Keep only lots with requested GHG reduction
                if ges_bound_min is not None and ges_bound_max is not None:
                    if detail.lot.ghg_reduction_red_ii <= float(ges_bound_min) or detail.lot.ghg_reduction_red_ii >= float(
                        ges_bound_max
                    ):
                        continue

                key = BalanceService._get_key(operation, group_by, detail, depot)

                if group_by != BalanceService.GROUP_BY_CATEGORY:
                    balance[key]["sector"] = operation.sector

                if group_by != BalanceService.GROUP_BY_SECTOR:
                    balance[key]["customs_category"] = operation.customs_category
                    if group_by != BalanceService.GROUP_BY_CATEGORY:
                        balance[key]["biofuel"] = operation.biofuel

                if not (credit_operation and operation.status == Operation.PENDING):
                    # Update available balance
                    BalanceService._update_available_balance(
                        balance, key, operation, detail, credit_operation, conversion_factor
                    )

                    # Update quantity and teneur only if the operation date is after the date_from
                    if date_from is None or operation.created_at >= date_from:
                        BalanceService._update_quantity_and_teneur(
                            balance, key, operation, detail, credit_operation, conversion_factor
                        )

                # Update GHG reduction min and max values
                if group_by not in BalanceService.GROUP_BY_ALL:
                    BalanceService._update_ghg_min_max(balance, key, detail)

            if "key" in locals() is not None and operation.status == Operation.PENDING:
                balance[key]["pending_operations"] += 1

        if group_by == BalanceService.GROUP_BY_DEPOT:
            balance = BalanceService._update_depot_debit_with_teneur_and_transfert(entity_id, balance, operations)

        return balance

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
                            remaining_volume -= volume_to_debit

        return balance
