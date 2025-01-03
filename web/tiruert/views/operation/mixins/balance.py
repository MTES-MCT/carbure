from datetime import datetime

from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.filters import OperationFilter
from tiruert.serializers import BalanceByLotSerializer, BalanceSerializer
from tiruert.services.balance import BalanceService


class BalanceActionMixin:
    @action(
        detail=False,
        methods=["get"],
        serializer_class=BalanceSerializer,
        filterset_class=OperationFilter,
    )
    def balance(self, request, pk=None):
        entity_id = request.query_params.get("entity_id")
        group_by = request.query_params.get("group_by", "")
        date_from = request.query_params.get("date_from")
        operations = OperationFilter(request.GET, queryset=self.get_queryset()).qs

        # Beginning of the current year by default
        if not date_from:
            current_year = datetime.now().year
            date_from = f"{current_year}-01-01"
            operations = operations.filter(created_at__gte=date_from)

        # Calculate the balance
        balance = BalanceService.calculate_balance(operations, entity_id, group_by)

        # Add initial balance to the balance (can't be done for lot)
        if group_by != "lot":
            balance = BalanceService.calculate_initial_balance(balance, entity_id, date_from, group_by)

        # Convert balance to a list of dictionaries for serialization
        if group_by == "lot":
            data = BalanceByLotSerializer.prepare_data(balance)
            serializer = BalanceByLotSerializer(data, many=True)
        else:
            data = list(balance.values())
            serializer = BalanceSerializer(data, many=True)

        return Response(serializer.data)
