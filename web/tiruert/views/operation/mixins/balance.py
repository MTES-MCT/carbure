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
        by_lot = request.query_params.get("by_lot", "0") == "1"
        date_from = request.query_params.get("date_from")
        operations = OperationFilter(request.GET, queryset=self.get_queryset()).qs

        # Calculate the balance
        balance = BalanceService.calculate_balance(operations, entity_id, by_lot)

        # Add initial balance to the balance if needed
        if date_from:
            balance = BalanceService.calculate_initial_balance(balance, entity_id, date_from)
            by_lot = False

        # Convert balance to a list of dictionaries for serialization
        if by_lot:
            data = BalanceByLotSerializer.transform_balance_data(balance, entity_id)
            serializer = BalanceByLotSerializer(data, many=True)
        else:
            data = BalanceSerializer.transform_balance_data(balance, entity_id)
            serializer = BalanceSerializer(data, many=True)

        return Response(serializer.data)
