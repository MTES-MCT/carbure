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
    BalanceBySectorSerializer,
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
            )
        ],
        responses={
            status.HTTP_200_OK: PolymorphicProxySerializer(
                many=True,
                component_name="BalanceResponse",
                serializers=[
                    BalanceSerializer,
                    BalanceByDepotSerializer,
                    BalanceBySectorSerializer,
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
        entity_id = request.entity.id
        group_by = request.query_params.get("group_by", "")
        unit = request.unit
        date_from_str = request.query_params.get("date_from")
        date_from = make_aware(datetime.strptime(date_from_str, "%Y-%m-%d")) if date_from_str else None

        operations = self.filter_queryset(self.get_queryset())

        if date_from:
            operations_with_date_from = operations
            # Remove date_from filter from operations
            query_params = request.GET.copy()
            query_params.pop("date_from", None)
            filterset = self.filterset_class(data=query_params, queryset=self.get_queryset(), request=request)
            operations = filterset.qs

        # First get the whole balance (from forever), so with no date_from filter
        balance = BalanceService.calculate_balance(operations, entity_id, group_by, unit)

        # Then update the balance with quantity and teneur details for requested dates (if any)
        operations = operations_with_date_from if date_from else operations
        balance = BalanceService.calculate_balance(operations, entity_id, group_by, unit, balance, update_balance=True)

        # Convert balance to a list of dictionaries for serialization
        serializer_class = {
            "lot": BalanceByLotSerializer,
            "depot": BalanceByDepotSerializer,
            "sector": BalanceBySectorSerializer,
        }.get(group_by, self.get_serializer_class())

        data = serializer_class.prepare_data(balance) if group_by in ["lot", "depot"] else list(balance.values())

        paginator = PageNumberPagination()
        paginated_data = paginator.paginate_queryset(data, request)

        serializer = serializer_class(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)
