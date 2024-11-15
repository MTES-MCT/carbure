from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.models import (
    CarbureLot,
    CarbureLotEvent,
    CarbureStock,
    CarbureStockTransformation,
    Entity,
)


class CancelErrors:
    MISSING_LOT_IDS = "MISSING_LOT_IDS"
    CANCEL_ACCEPT_NOT_ALLOWED = "CANCEL_ACCEPT_NOT_ALLOWED"
    NOT_LOT_CLIENT = "NOT_LOT_CLIENT"
    WRONG_STATUS = "WRONG_STATUS"
    CHILDREN_IN_USE = "CHILDREN_IN_USE"


class CancelAcceptSerializer(serializers.Serializer):
    # config fields
    lot_ids = serializers.PrimaryKeyRelatedField(queryset=CarbureLot.objects.all(), many=True)


class CancelAcceptMixin:
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
        request=CancelAcceptSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False, url_path="cancel-accept")
    def cancel_accept(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")

        serializer = CancelAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lots = serializer.validated_data["lot_ids"]

        entity = get_object_or_404(Entity, id=entity_id)

        for lot in lots:
            if lot.carbure_client != entity:
                raise PermissionDenied({"message": CancelErrors.NOT_LOT_CLIENT})

            if lot.lot_status in (
                CarbureLot.DRAFT,
                CarbureLot.PENDING,
                CarbureLot.REJECTED,
                CarbureLot.FROZEN,
                CarbureLot.DELETED,
            ):
                raise ValidationError({"message": CancelErrors.WRONG_STATUS})

            # delete new lots created when the lot was accepted
            if lot.delivery_type in (CarbureLot.PROCESSING, CarbureLot.TRADING):
                children_lots = CarbureLot.objects.filter(parent_lot=lot).exclude(lot_status__in=[CarbureLot.DELETED])
                # do not do anything if the children lots are already used

                if children_lots.filter(lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN]).count() > 0:
                    raise ValidationError({"message": CancelErrors.CHILDREN_IN_USE})
                else:
                    children_lots.delete()

            # delete new stocks created when the lot was accepted
            if lot.delivery_type == CarbureLot.STOCK:
                children_stocks = CarbureStock.objects.filter(parent_lot=lot)
                children_stocks_children_lots = CarbureLot.objects.filter(parent_stock__in=children_stocks).exclude(
                    lot_status=CarbureLot.DELETED
                )
                children_stocks_children_trans = CarbureStockTransformation.objects.filter(source_stock__in=children_stocks)
                # do not do anything if the children stocks are already used
                if children_stocks_children_lots.count() > 0 or children_stocks_children_trans.count() > 0:
                    raise ValidationError({"message": CancelErrors.CHILDREN_IN_USE})
                else:
                    children_stocks.delete()

            lot.lot_status = CarbureLot.PENDING
            lot.delivery_type = CarbureLot.UNKNOWN
            lot.save()
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.CANCELLED
            event.lot = lot
            event.user = request.user
            event.save()
        return Response({"status": "success"})
