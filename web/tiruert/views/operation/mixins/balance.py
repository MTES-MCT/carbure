from datetime import datetime

from django.utils.timezone import make_aware
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
        date_from_str = request.query_params.get("date_from")
        date_from = make_aware(datetime.strptime(date_from_str, "%Y-%m-%d")) if date_from_str else None
        operations = self.filter_queryset(self.get_queryset())

        # Beginning of the current year by default
        if not date_from and group_by != "lot":
            current_year = datetime.now().year
            date_from = make_aware(datetime(current_year, 1, 1))
            operations = operations.filter(created_at__gte=date_from)

        # Calculate the balance
        balance = BalanceService.calculate_balance(operations, entity_id, group_by)

        # Add initial balance and yearly teneur to the balance (can't be done for lot)
        if group_by != "lot":
            balance = BalanceService.calculate_initial_balance(balance, entity_id, date_from, group_by)
            balance = BalanceService.calculate_yearly_teneur(balance, entity_id, date_from, group_by)

        # Convert balance to a list of dictionaries for serialization
        if group_by == "lot":
            serializer_class = BalanceByLotSerializer
            data = serializer_class.prepare_data(balance)
        else:
            data = list(balance.values())
            serializer_class = self.get_serializer_class()

        serializer = serializer_class(data, many=True)
        return Response(serializer.data)
