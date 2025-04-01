from collections import defaultdict
from functools import partial

from tiruert.models import Operation


class BalanceService:
    GROUP_BY_SECTOR = "sector"
    GROUP_BY_CATEGORY = "customs_category"
    GROUP_BY_LOT = "lot"
    GROUP_BY_DEPOT = "depot"

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
        }

        return entry

    def _update_quantity_and_teneur(balance, key, operation, detail, entity_id, conversion_factor):
        """
        Updates the balance entry with the details of the operation
        """
        if operation.type == Operation.TENEUR:
            teneur_type = "pending_teneur" if operation.status == Operation.PENDING else "declared_teneur"
            balance[key][teneur_type] += detail.volume * conversion_factor

        quantity_type = "credit" if operation.is_credit(entity_id) else "debit"
        balance[key]["quantity"][quantity_type] += detail.volume * conversion_factor

        return balance

    def _update_available_balance(balance, key, operation, detail, entity_id, conversion_factor):
        """
        Updates the balance entry with the details of the operation
        """
        volume_sign = 1 if operation.is_credit(entity_id) else -1
        balance[key]["available_balance"] += detail.volume * volume_sign * conversion_factor
        balance[key]["emission_rate_per_mj"] = detail.emission_rate_per_mj
        return

    @staticmethod
    def calculate_balance(operations, entity_id, group_by, unit, date_from=None):
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
            if operation.is_credit(entity_id) and operation.status == Operation.PENDING:
                continue

            depot = operation.to_depot if operation.is_credit(entity_id) else operation.from_depot
            if depot is None:
                continue

            conversion_factor = BalanceService._get_conversion_factor(operation, unit)

            for detail in operation.details.all():
                key = BalanceService._get_key(operation, group_by, detail, depot)

                if group_by != BalanceService.GROUP_BY_CATEGORY:
                    balance[key]["sector"] = operation.sector

                if group_by != BalanceService.GROUP_BY_SECTOR:
                    balance[key]["customs_category"] = operation.customs_category
                    if group_by != BalanceService.GROUP_BY_CATEGORY:
                        balance[key]["biofuel"] = operation.biofuel

                # Update available balance
                BalanceService._update_available_balance(balance, key, operation, detail, entity_id, conversion_factor)

                # Update quantity and teneur only if the operation date is after the date_from
                if date_from is None or operation.created_at >= date_from:
                    BalanceService._update_quantity_and_teneur(balance, key, operation, detail, entity_id, conversion_factor)

            if operation.status == Operation.PENDING:
                balance[key]["pending_operations"] += 1

        if group_by == BalanceService.GROUP_BY_DEPOT:
            teneurs_per_depots = BalanceService._get_teneur_per_depot(entity_id)
            for key, volume in teneurs_per_depots.items():
                balance[key]["quantity"]["debit"] += volume

        return balance

    @staticmethod
    def _get_teneur_per_depot(entity_id):
        """
        Returns a dictionary with the total volume of teneur operations per depot
        """
        teneurs = Operation.objects.filter(
            debited_entity=entity_id,
            type=Operation.TENEUR,
            status__in=[Operation.PENDING, Operation.DECLARED],
        ).prefetch_related("details__lot")

        lot_ids = []
        for teneur in teneurs:
            for detail in teneur.details.all():
                lot_ids.append(detail.lot.id)

        credited_operations = {}
        operations_with_lots = (
            Operation.objects.filter(
                credited_entity=entity_id,
                details__lot_id__in=lot_ids,
                status__in=[Operation.VALIDATED, Operation.ACCEPTED, Operation.CORRECTED],
            )
            .prefetch_related("details__lot")
            .order_by("details__lot_id", "-created_at")
        )

        for operation in operations_with_lots:
            for detail in operation.details.all():
                if detail.lot_id in lot_ids:
                    if detail.lot_id not in credited_operations:
                        credited_operations[detail.lot_id] = {
                            "operation": operation,
                            "depot": operation.to_depot,
                        }

        teneur_per_depot = {}
        for teneur in teneurs:
            for detail in teneur.details.all():
                if detail.lot_id in credited_operations:
                    depot_key = credited_operations[detail.lot_id]["depot"]
                    key = (teneur.sector, teneur.customs_category, teneur.biofuel.code, depot_key)

                    if key not in teneur_per_depot:
                        teneur_per_depot[key] = 0

                    teneur_per_depot[key] += detail.volume

        return teneur_per_depot
