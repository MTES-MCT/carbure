from collections import defaultdict
from datetime import datetime

from django.db.models import Q

from tiruert.models import Operation


class BalanceService:
    @staticmethod
    def calculate_balance(operations, entity_id, group_by):
        """
        Keep only PENDING and ACCEPTED operations
        Group by sector, customs_category and biofuel (and lot if needed)
        Sum volume: credit when entity is credited, debit when entity is debited
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
            }
        )

        operations = operations.filter(status__in=[Operation.PENDING, Operation.ACCEPTED])

        for operation in operations:
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
                    balance[key]["teneur"] += detail.volume
                else:
                    if operation.is_credit(entity_id):
                        balance[key]["volume"]["credit"] += detail.volume
                    else:
                        balance[key]["volume"]["debit"] += detail.volume

            if key and group_by != "lot" and operation.status == Operation.PENDING:
                balance[key]["pending"] += 1

        return balance

    @staticmethod
    def calculate_initial_balance(balance, entity_id, until_date, group_by):
        """
        Calculate initial balances for the given entity until the given date
        and add them to the balance dict
        """
        operations = Operation.objects.filter(
            created_at__lt=until_date,
            status__in=[Operation.PENDING, Operation.ACCEPTED],
        ).filter((Q(credited_entity_id=entity_id) | Q(debited_entity_id=entity_id)))

        initial_balances = defaultdict(int)

        for operation in operations:
            key, balance = BalanceService.set_keys_and_initial_balance(operation, balance, group_by)

            for detail in operation.details.all():
                initial_balances[key] += detail.volume if operation.is_credit(entity_id) else -detail.volume

        for key in balance:
            balance[key]["initial_balance"] = initial_balances[key]

        return balance

    @staticmethod
    def calculate_yearly_teneur(balance, entity_id, until_date, group_by):
        """
        Calculate yearly teneur for the given entity, from the beginning of the year
        to the until_date given, and add them to the balance dict
        """

        current_year = datetime.now().year
        if until_date == datetime(current_year, 1, 1):  # No need to calculate yearly teneur
            return balance

        beginning_of_year = datetime(until_date.year, 1, 1)

        operations = Operation.objects.filter(
            created_at__gte=beginning_of_year,
            created_at__lt=until_date,
            status__in=[Operation.PENDING, Operation.ACCEPTED],  # Faut il garder les teneurs PENDING ?
            type=Operation.TENEUR,
            debited_entity_id=entity_id,
        )

        yearly_teneurs = defaultdict(int)

        for operation in operations:
            key, balance = BalanceService.set_keys_and_initial_balance(operation, balance, group_by)

            for detail in operation.details.all():
                yearly_teneurs[key] += detail.volume

        for key in balance:
            balance[key]["yearly_teneur"] = yearly_teneurs[key]

        return balance

    @staticmethod
    def set_keys_and_initial_balance(operation, balance, group_by):
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
            }
            if group_by != "sector":
                balance[key]["customs_category"] = operation.customs_category
                balance[key]["biofuel"] = operation.biofuel.code

        return key, balance
