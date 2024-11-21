from collections import defaultdict

from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.filters import OperationFilter
from tiruert.serializers import BalanceByLotSerializer, BalanceSerializer


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
        operations = OperationFilter(request.GET, queryset=self.get_queryset()).qs

        # Group by customs_category and biofuel
        # Sum energy: credit when entity is credited, debit when entity is debited
        balance = defaultdict(lambda: {"credit": 0, "debit": 0})
        for operation in operations:
            grouped_by = (operation.customs_category, operation.biofuel)
            for detail in operation.details.all():
                key = grouped_by
                if by_lot:
                    key = grouped_by + (detail.lot.id,)

                # Get the balance for this key
                detail_balance = balance[key]

                if operation.is_credit(entity_id):
                    # Add the energy of the detail to the balance
                    detail_balance["credit"] += detail.energy
                else:
                    detail_balance["debit"] += detail.energy

        # Convert the balance to a list of dictionaries for serialization
        if by_lot:
            data = BalanceByLotSerializer.transform_balance_data(balance, entity_id)
            serializer = BalanceByLotSerializer(data, many=True)
        else:
            data = BalanceSerializer.transform_balance_data(balance, entity_id)
            serializer = BalanceSerializer(data, many=True)

        return Response(serializer.data)
