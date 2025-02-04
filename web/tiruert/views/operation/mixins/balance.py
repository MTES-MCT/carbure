from datetime import datetime

from django.utils.timezone import make_aware
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from tiruert.filters import OperationFilter
from tiruert.serializers import BalanceByLotSerializer, BalanceSerializer, PaginatedBalanceSerializer
from tiruert.services.balance import BalanceService


class BalanceActionMixin:
    @extend_schema(
        operation_id="list_balances",
        description="Retrieve balances grouped by mp category / biofuel or by sector",
        filters=True,
        parameters=[
            OpenApiParameter(
                name="group_by",
                type=str,
                enum=["sector", "lot"],
                location=OpenApiParameter.QUERY,
                description="Group by sector or by lot.",
                default="",
            ),
            OpenApiParameter(
                name="unit",
                type=str,
                enum=["l", "mj"],
                location=OpenApiParameter.QUERY,
                description="Specify the volume unit (default is `l`).",
                default="l",
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=PaginatedBalanceSerializer,
                description="Paginated response with balances grouped by mp category / biofuel or by sector",
            )
        },
    )
    @action(
        detail=False,
        methods=["get"],
        serializer_class=BalanceSerializer,
        filterset_class=OperationFilter,
        pagination_class=PageNumberPagination,
    )
    def balance(self, request, pk=None):
        entity_id = request.query_params.get("entity_id")
        group_by = request.query_params.get("group_by", "")
        date_from_str = request.query_params.get("date_from")
        date_from = make_aware(datetime.strptime(date_from_str, "%Y-%m-%d")) if date_from_str else None
        unit = request.query_params.get("unit", "l")
        operations = self.filter_queryset(self.get_queryset())

        # Beginning of the current year by default
        if not date_from and group_by != "lot":
            current_year = datetime.now().year
            date_from = make_aware(datetime(current_year, 1, 1))
            operations = operations.filter(created_at__gte=date_from)

        # Calculate the balance
        balance = BalanceService.calculate_balance(operations, entity_id, group_by, unit)

        # Add initial balance and yearly teneur to the balance (can't be done for lot)
        if group_by != "lot":
            balance = BalanceService.calculate_initial_balance(balance, entity_id, date_from, group_by, unit)
            balance = BalanceService.calculate_yearly_teneur(balance, entity_id, date_from, group_by, unit)

        # Convert balance to a list of dictionaries for serialization
        if group_by == "lot":
            serializer_class = BalanceByLotSerializer
            data = serializer_class.prepare_data(balance)
        else:
            data = list(balance.values())
            serializer_class = self.get_serializer_class()

        paginator = PageNumberPagination()
        paginated_data = paginator.paginate_queryset(data, request)

        serializer = serializer_class(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)
