from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import (
    CarbureStock,
    CarbureStockEvent,
    CarbureStockTransformation,
    Entity,
)


class StockCancelTransformationSerializer(serializers.Serializer):
    stock_ids = serializers.ListField(child=serializers.IntegerField(), required=True)

    def validate_stock_ids(self, value):
        if not value:
            raise serializers.ValidationError("The stock_id list must not be empty.")
        return value


class CancelTransformationMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        request=StockCancelTransformationSerializer,
        examples=[
            OpenApiExample(
                "Example of response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False, url_path="cancel-transformation")
    def cancel_transformation(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)

        serializer = StockCancelTransformationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stock_ids = serializer.validated_data["stock_ids"]

        stocks = (
            CarbureStock.objects.filter(pk__in=stock_ids, carbure_client=entity)
            .exclude(parent_transformation=None)
            .select_related("parent_transformation", "parent_transformation__source_stock")
        )

        with transaction.atomic():
            stock_events = []
            stocks_to_update = set()

            stock_transformations = [s.parent_transformation for s in stocks]

            for transform in stock_transformations:
                transform.source_stock.update_remaining_volume(+transform.volume_deducted_from_source)

                stocks_to_update.add(transform.source_stock)

                stock_events.append(
                    CarbureStockEvent(
                        stock=transform.source_stock,
                        event_type=CarbureStockEvent.UNTRANSFORMED,
                        user=request.user,
                    )
                )

            CarbureStockEvent.objects.bulk_create(stock_events)
            CarbureStock.objects.bulk_update(
                stocks_to_update,
                ["remaining_volume", "remaining_weight", "remaining_lhv_amount"],
            )
            CarbureStockTransformation.objects.filter(id__in=[t.id for t in stock_transformations]).delete()

        return Response({"status": "success"})
