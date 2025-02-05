from collections import defaultdict
from datetime import datetime

from django.utils.timezone import make_aware

from tiruert.models import Operation


class BalanceService:
    @staticmethod
    def calculate_balance(operations, entity_id, group_by, unit="l"):
        """
        Keep only PENDING and ACCEPTED operations
        Group by sector, customs_category and biofuel (and lot if needed)
        Sum volume: credit when entity is credited, debit when entity is debited
        For credit operation, if PENDING, don't sum volume
        For debit operation, if PENDING, sum volume
        """

        balance = defaultdict(
            lambda: {
                "sector": None,
                "customs_category": None,
                "biofuel": None,
                "volume": {"credit": 0, "debit": 0},
                "emission_rate_per_mj": 0,
                "teneur": 0,
                "pending": 0,
                "unit": "l",
            }
        )
        key = None

        operations = operations.filter(status__in=[Operation.PENDING, Operation.ACCEPTED])

        for operation in operations:
            if operation.is_credit(entity_id) and operation.status == Operation.PENDING:
                continue

            pci = operation.biofuel.pci_litre if unit == "mj" else 1  # pci = 1 if unit is in litres

            for detail in operation.details.all():
                key = (operation.sector, operation.customs_category, operation.biofuel.code)

                if group_by == "lot":
                    key = key + (detail.lot.id,)

                if group_by == "sector":
                    key = operation.sector

                balance[key]["sector"] = operation.sector
                if group_by != "sector":
                    balance[key]["customs_category"] = operation.customs_category
                    balance[key]["biofuel"] = operation.biofuel.code

                balance[key]["emission_rate_per_mj"] = detail.emission_rate_per_mj

                if operation.type == Operation.TENEUR and group_by != "lot":
                    balance[key]["teneur"] += detail.volume * pci
                else:
                    if operation.is_credit(entity_id):
                        balance[key]["volume"]["credit"] += detail.volume * pci
                    else:
                        balance[key]["volume"]["debit"] += detail.volume * pci

            if key and group_by != "lot" and operation.status == Operation.PENDING:
                balance[key]["pending"] += 1

            balance[key]["unit"] = unit

        return balance

    @staticmethod
    def calculate_initial_balance(balance, entity_id, operations, group_by, unit="l"):
        """
        Calculate initial balances for the given entity until the given date
        and add them to the balance dict
        """
        initial_balances = defaultdict(int)

        for operation in operations:
            key, balance = BalanceService.set_keys_and_initial_balance(operation, balance, group_by, unit)
            pci = operation.biofuel.pci_litre if unit == "mj" else 1

            for detail in operation.details.all():
                initial_balances[key] += (detail.volume if operation.is_credit(entity_id) else -detail.volume) * pci

        for key in balance:
            balance[key]["initial_balance"] = initial_balances[key]

        return balance

    @staticmethod
    def calculate_yearly_teneur(balance, entity_id, operations, until_date, group_by, unit="l"):
        """
        Calculate yearly teneur for the given entity, from the beginning of the year
        to the until_date given, and add them to the balance dict
        """

        beginning_of_year = make_aware(datetime(until_date.year, 1, 1))

        if until_date == beginning_of_year:  # No need to calculate yearly teneur
            return balance

        operations = operations.filter(
            created_at__gte=beginning_of_year,
            type=Operation.TENEUR,
            debited_entity_id=entity_id,
        )

        yearly_teneurs = defaultdict(int)

        for operation in operations:
            key, balance = BalanceService.set_keys_and_initial_balance(operation, balance, group_by, unit)
            pci = operation.biofuel.pci_litre if unit == "mj" else 1

            for detail in operation.details.all():
                yearly_teneurs[key] += detail.volume * pci

        for key in balance:
            balance[key]["yearly_teneur"] = yearly_teneurs[key]

        return balance

    @staticmethod
    def set_keys_and_initial_balance(operation, balance, group_by, unit):
        key = (
            operation.sector
            if group_by == "sector"
            else (operation.sector, operation.customs_category, operation.biofuel.code)
        )

        # Handle the case where there are operations for a specific biofuel before the requested date, but
        # no operations after
        # In this case, the key won't be in the balance dict
        if key not in balance:
            balance[key] = {
                "volume": {"credit": 0, "debit": 0},
                "emission_rate_per_mj": 0,
                "pending": 0,
                "sector": operation.sector,
                "teneur": 0,
                "yearly_teneur": 0,
                "initial_balance": 0,
                "unit": unit,
            }
            if group_by != "sector":
                balance[key]["customs_category"] = operation.customs_category
                balance[key]["biofuel"] = operation.biofuel.code

        return key, balance
