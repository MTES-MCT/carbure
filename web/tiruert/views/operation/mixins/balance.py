from datetime import datetime

from django.utils.timezone import make_aware
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, PolymorphicProxySerializer, extend_schema
from rest_framework import status
from rest_framework.decorators import action

from core.pagination import MetadataPageNumberPagination
from tiruert.filters import OperationFilterForBalance
from tiruert.serializers import (
    BalanceByDepotSerializer,
    BalanceByLotSerializer,
    BalanceBySectorSerializer,
    BalanceSerializer,
)
from tiruert.services.balance import BalanceService


class BalancePagination(MetadataPageNumberPagination):
    aggregate_fields = {"total_quantity": 0}

    def get_extra_metadata(self):
        metadata = {"total_quantity": 0}

        for balance in self.queryset:
            metadata["total_quantity"] += balance["available_balance"]
        return metadata


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
                name="date_from",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Date from where to calculate teneur and quantity",
                default=None,
            ),
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
        filterset_class=OperationFilterForBalance,
        pagination_class=BalancePagination,
    )
    def balance(self, request, pk=None):
        entity_id = request.entity.id
        unit = request.unit
        group_by = request.query_params.get("group_by", "")
        date_from_str = request.query_params.get("date_from")
        date_from = make_aware(datetime.strptime(date_from_str, "%Y-%m-%d")) if date_from_str else None

        operations = self.filter_queryset(self.get_queryset())

        balance = BalanceService.calculate_balance(operations, entity_id, group_by, unit, date_from)

        # Convert balance to a list of dictionaries for serialization
        serializer_class = {
            "lot": BalanceByLotSerializer,
            "depot": BalanceByDepotSerializer,
            "sector": BalanceBySectorSerializer,
        }.get(group_by, self.get_serializer_class())

        data = serializer_class.prepare_data(balance) if group_by in ["lot", "depot"] else list(balance.values())

        paginator = BalancePagination()
        paginated_data = paginator.paginate_queryset(data, request)

        serializer = serializer_class(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)
