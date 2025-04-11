from typing import TypedDict

from django.db.models import QuerySet

from tiruert.models import ElecOperation


class ElecBalance(TypedDict):
    quantity: dict
    emission_rate_per_mj: float
    pending_teneur: int
    pending_operations: int
    declared_teneur: int
    available_balance: int


class ElecBalanceService:
    @staticmethod
    def _init_balance_entry() -> ElecBalance:
        """
        Initializes a balance entry with default values
        """
        entry = {
            "quantity": {"credit": 0, "debit": 0},
            "emission_rate_per_mj": 0,
            "pending_teneur": 0,
            "pending_operations": 0,
            "declared_teneur": 0,
            "available_balance": 0,
        }

        return entry

    def _update_quantity_and_teneur(balance: ElecBalance, operation: ElecOperation, entity_id):
        """
        Updates the balance entry with the operation
        """
        if operation.type == ElecOperation.TENEUR:
            teneur_type = "pending_teneur" if operation.status == ElecOperation.PENDING else "declared_teneur"
            balance[teneur_type] += operation.quantity

        quantity_type = "credit" if operation.is_credit(entity_id) else "debit"
        balance["quantity"][quantity_type] += operation.quantity

        return balance

    def _update_available_balance(balance: ElecBalance, operation: ElecOperation, entity_id):
        """
        Updates the balance entry with the details of the operation
        """
        volume_sign = 1 if operation.is_credit(entity_id) else -1
        balance["available_balance"] += operation.quantity * volume_sign
        balance["emission_rate_per_mj"] = ElecOperation.EMISSION_RATE_PER_MJ
        return

    @staticmethod
    def calculate_balance(operations: QuerySet[ElecOperation], entity_id, date_from=None) -> ElecBalance:
        """
        Calculates balances based on the specified grouping
        'operations' is a queryset of already filtered operations
        """
        balance = ElecBalanceService._init_balance_entry()

        operations = operations.filter(status__in=[ElecOperation.PENDING, ElecOperation.ACCEPTED, ElecOperation.DECLARED])

        for operation in operations:
            if operation.is_credit(entity_id) and operation.status == ElecOperation.PENDING:
                continue

            ElecBalanceService._update_available_balance(balance, operation, entity_id)

            # Update quantity and teneur only if the operation date is after the date_from
            if date_from is None or operation.created_at >= date_from:
                ElecBalanceService._update_quantity_and_teneur(balance, operation, entity_id)

            if operation.status == ElecOperation.PENDING:
                balance["pending_operations"] += 1

        return balance
