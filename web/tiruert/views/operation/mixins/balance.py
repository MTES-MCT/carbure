from datetime import datetime

from django.utils.timezone import make_aware
from drf_spectacular.utils import OpenApiParameter, PolymorphicProxySerializer, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from tiruert.filters import OperationFilter
from tiruert.serializers import (
    BalanceByDepotSerializer,
    BalanceByLotSerializer,
    BalanceSerializer,
)
from tiruert.services.balance import BalanceService


class BalanceActionMixin:
    @extend_schema(
        operation_id="list_balances",
        description="Retrieve balances grouped by mp category / biofuel or by sector or by depot",
        filters=True,
        parameters=[
            OpenApiParameter(
                name="group_by",
                type=str,
                enum=["sector", "lot", "depot"],
                location=OpenApiParameter.QUERY,
                description="Group by sector, lot or depot.",
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
            status.HTTP_200_OK: PolymorphicProxySerializer(
                many=True,
                component_name="BalanceResponse",
                serializers=[
                    BalanceByDepotSerializer,
                    BalanceSerializer,
                ],
                resource_type_field_name=None,
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
        unit = request.query_params.get("unit", "l")

        date_from_str = request.query_params.get("date_from")
        date_from = make_aware(datetime.strptime(date_from_str, "%Y-%m-%d")) if date_from_str else None

        operations = self.filter_queryset(self.get_queryset())

        if group_by in ["lot", "depot"]:
            # Calculate the balance
            balance = BalanceService.calculate_balance(operations, entity_id, group_by, unit)

        else:
            if not date_from:
                # All operations from beginning of the current year by default
                current_year = datetime.now().year
                date_from = make_aware(datetime(current_year, 1, 1))
                operations = operations.filter(created_at__gte=date_from)

            # Calculate the balance
            balance = BalanceService.calculate_balance(operations, entity_id, group_by, unit)

            # Get operations again but this time until the date_from
            query_params = request.GET.copy()
            query_params.pop("date_from", None)
            filterset = self.filterset_class(data=query_params, queryset=self.get_queryset(), request=request)
            operations_without_date_filter = filterset.qs

            operations = operations_without_date_filter.filter(created_at__lt=date_from)

            # Add initial balance and yearly teneur to the balance
            balance = BalanceService.calculate_initial_balance(balance, entity_id, operations, group_by, unit)
            balance = BalanceService.calculate_yearly_teneur(balance, entity_id, operations, date_from, group_by, unit)

        # Convert balance to a list of dictionaries for serialization
        serializer_class = {
            "lot": BalanceByLotSerializer,
            "depot": BalanceByDepotSerializer,
        }.get(group_by, self.get_serializer_class())

        data = serializer_class.prepare_data(balance) if group_by in ["lot", "depot"] else list(balance.values())

        paginator = PageNumberPagination()
        paginated_data = paginator.paginate_queryset(data, request)

        serializer = serializer_class(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)
