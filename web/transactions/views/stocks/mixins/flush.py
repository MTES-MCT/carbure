from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.models import (
    CarbureLot,
    CarbureLotEvent,
    CarbureStock,
    CarbureStockEvent,
    Entity,
)


class StockFlushSerializer(serializers.Serializer):
    # config fields
    stock_ids = serializers.PrimaryKeyRelatedField(queryset=CarbureStock.objects.all(), many=True)
    free_field = serializers.CharField(required=False, allow_null=True, default=None)

    def validate_stock_ids(self, value):
        if not value:
            raise serializers.ValidationError("stock_ids must not be empty.")
        return value


class FlushMixin:
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
        request=StockFlushSerializer,
        examples=[
            OpenApiExample(
                "Example of response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False, serializer_class=StockFlushSerializer)
    def flush(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)

        serializer = StockFlushSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stocks = serializer.validated_data["stock_ids"]
        free_field = serializer.validated_data["free_field"]

        for stock in stocks:
            if stock.carbure_client_id != entity.id:
                raise PermissionDenied(
                    {"message": "Stock does not belong to you"},
                )

            volume_to_flush = stock.remaining_volume
            initial_volume = 0
            if stock.parent_lot:
                initial_volume = stock.parent_lot.volume
            elif stock.parent_transformation:
                initial_volume = stock.parent_transformation.volume_destination

            if volume_to_flush > initial_volume * 0.05:
                raise ValidationError({"message": "Cannot flush a stock with a remaining volume greater than 5%"})

            # update remaining stock
            rounded_volume = round(volume_to_flush, 2)
            if rounded_volume >= stock.remaining_volume:
                stock.remaining_volume = 0
                stock.remaining_weight = 0
                stock.remaining_lhv_amount = 0
            else:
                stock.remaining_volume = round(stock.remaining_volume - rounded_volume, 2)
                stock.remaining_weight = stock.get_weight()
                stock.remaining_lhv_amount = stock.get_lhv_amount()
            stock.save()

            # create flushed lot
            lot = stock.get_parent_lot()
            lot.pk = None
            lot.transport_document_type = CarbureLot.OTHER
            lot.transport_document_reference = "N/A - FLUSH"
            lot.volume = rounded_volume
            lot.weight = lot.get_weight()
            lot.lhv_amount = lot.get_lhv_amount()
            lot.lot_status = CarbureLot.ACCEPTED
            lot.delivery_type = CarbureLot.FLUSHED
            lot.unknown_client = None
            lot.carbure_delivery_site = None
            lot.unknown_delivery_site = None
            lot.delivery_site_country = None
            lot.parent_lot = None
            lot.parent_stock = stock
            if free_field:
                lot.free_field = free_field
            else:
                lot.free_field = "FLUSHED"
            lot.save()
            # create events
            e = CarbureStockEvent()
            e.event_type = CarbureStockEvent.FLUSHED
            e.user = request.user
            e.stock = stock
            e.save()
            e = CarbureLotEvent()
            e.event_type = CarbureLotEvent.CREATED
            e.lot = lot
            e.user = request.user
            e.save()
            e.pk = None
            e.event_type = CarbureLotEvent.ACCEPTED
            e.save()
        return Response({"status": "success"})
