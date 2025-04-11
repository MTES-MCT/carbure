from datetime import datetime

from django.utils.timezone import make_aware
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.decorators import action

from core.pagination import MetadataPageNumberPagination
from tiruert.filters.elec_operation import ElecOperationFilter
from tiruert.serializers import ElecBalanceSerializer
from tiruert.services.elec_balance import ElecBalanceService


class ElecBalancePagination(MetadataPageNumberPagination):
    aggregate_fields = {"total_quantity": 0}

    def get_extra_metadata(self):
        metadata = {"total_quantity": 0}
        for balance in self.queryset:
            metadata["total_quantity"] += balance["available_balance"]
        return metadata


class BalanceActionMixin:
    @extend_schema(
        operation_id="list_elec_balance",
        description="Retrieve electricity balance",
        filters=True,
        parameters=[
            OpenApiParameter(
                name="date_from",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Date from when to calculate teneur and quantity",
                default=None,
            ),
        ],
        responses=ElecBalanceSerializer(many=True),
    )
    @action(
        detail=False,
        methods=["get"],
        serializer_class=ElecBalanceSerializer,
        filterset_class=ElecOperationFilter,
        pagination_class=ElecBalancePagination,
    )
    def balance(self, request, pk=None):
        entity_id = request.entity.id
        date_from_str = request.query_params.get("date_from")
        date_from = make_aware(datetime.strptime(date_from_str, "%Y-%m-%d")) if date_from_str else None

        operations = self.filter_queryset(self.get_queryset())

        data = ElecBalanceService.calculate_balance(operations, entity_id, date_from)

        paginator = ElecBalancePagination()
        paginated_data = paginator.paginate_queryset([data], request)

        serializer = ElecBalanceSerializer(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)
