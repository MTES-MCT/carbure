from typing import TypedDict

from django.db.models import QuerySet, Sum

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
    def total(operations: QuerySet[ElecOperation]):
        return operations.aggregate(Sum("quantity")).get("quantity__sum") or 0

    @staticmethod
    def calculate_balance(operations: QuerySet[ElecOperation], entity_id, date_from=None) -> ElecBalance:
        """
        Calculates balances based on the specified grouping
        'operations' is a queryset of already filtered operations
        """

        operations = operations.filter(status__in=[ElecOperation.PENDING, ElecOperation.ACCEPTED, ElecOperation.DECLARED])
        pending_operations = operations.filter(status=ElecOperation.PENDING)

        credited_operations = operations.filter(
            type__in=[ElecOperation.CESSION, ElecOperation.ACQUISITION_FROM_CPO],
            status__in=[ElecOperation.ACCEPTED],
            credited_entity_id=entity_id,
        )

        debited_operations = operations.filter(
            type__in=[ElecOperation.CESSION, ElecOperation.TENEUR],
            status__in=[ElecOperation.PENDING, ElecOperation.ACCEPTED, ElecOperation.DECLARED],
            debited_entity_id=entity_id,
        )

        pending_teneur = operations.filter(
            type=ElecOperation.TENEUR,
            status=ElecOperation.PENDING,
            debited_entity_id=entity_id,
        )

        declared_teneur = operations.filter(
            type=ElecOperation.TENEUR,
            status=ElecOperation.DECLARED,
            debited_entity_id=entity_id,
        )

        period_credited_operations = credited_operations
        period_debited_operations = debited_operations

        if date_from:
            period_credited_operations = period_credited_operations.filter(created_at__gte=date_from)
            period_debited_operations = period_debited_operations.filter(created_at__gte=date_from)
            pending_teneur = pending_teneur.filter(created_at__gte=date_from)
            declared_teneur = declared_teneur.filter(created_at__gte=date_from)

        total_credit = ElecBalanceService.total(credited_operations)
        total_debit = ElecBalanceService.total(debited_operations)

        return {
            "sector": ElecOperation.SECTOR,
            "quantity": {
                "credit": ElecBalanceService.total(period_credited_operations),
                "debit": ElecBalanceService.total(period_debited_operations),
            },
            "emission_rate_per_mj": ElecOperation.EMISSION_RATE_PER_MJ,
            "pending_operations": pending_operations.count(),
            "pending_teneur": ElecBalanceService.total(pending_teneur),
            "declared_teneur": ElecBalanceService.total(declared_teneur),
            "available_balance": total_credit - total_debit,
        }
