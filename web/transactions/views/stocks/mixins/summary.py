import traceback

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.helpers import get_stocks_summary_data
from core.models import Entity


class StockSummarySerializer(serializers.Serializer):
    supplier = serializers.CharField()
    biofuel_code = serializers.CharField()
    remaining_volume_sum = serializers.FloatField()
    remaining_weight_sum = serializers.FloatField()
    remaining_lhv_amount_sum = serializers.FloatField()
    avg_ghg_reduction = serializers.FloatField()
    total = serializers.IntegerField()


class StocksSummaryResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    total_remaining_volume = serializers.FloatField()
    total_remaining_weight = serializers.FloatField()
    total_remaining_lhv_amount = serializers.FloatField()
    stock = StockSummarySerializer(many=True)


class SummaryMixin:
    @extend_schema(
        filters=True,
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        responses=StocksSummaryResponseSerializer,
    )
    @action(methods=["get"], detail=False)
    def summary(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        short = self.request.query_params.get("short", False)
        entity = Entity.objects.get(id=entity_id)
        stock = self.filter_queryset(self.get_queryset())
        try:
            if entity.entity_type == Entity.ADMIN:
                entity_id = None
            summary = get_stocks_summary_data(stock, entity_id, short == "true")
            return Response(summary)
        except Exception:
            traceback.print_exc()
            return Response(
                {"message": "Could not get stock summary"},
                status=status.HTTP_400_BAD_REQUEST,
            )
