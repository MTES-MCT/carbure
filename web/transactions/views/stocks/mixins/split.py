from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.models import (
    CarbureLot,
    CarbureLotEvent,
    CarbureStock,
    CarbureStockEvent,
    Entity,
    Pays,
)
from transactions.helpers import try_get_date
from transactions.models import Depot
from transactions.sanity_checks import get_prefetched_data


class SplitResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="success")
    data = serializers.ListField(child=serializers.IntegerField())


class SplitCreateSerializer(serializers.Serializer):
    stock_id = serializers.CharField(max_length=255)
    volume = serializers.FloatField()
    delivery_date = serializers.DateField()
    supplier_certificate = serializers.CharField(max_length=255, required=False)
    dispatch_date = serializers.DateField(required=False)
    unknown_client = serializers.CharField(max_length=255, required=False)
    unknown_delivery_site = serializers.CharField(max_length=255, required=False)
    delivery_site_country_id = serializers.CharField(max_length=255, required=False)
    transport_document_type = serializers.CharField(max_length=100, required=False)
    delivery_type = serializers.CharField(max_length=100, required=False)
    transport_document_reference = serializers.CharField(max_length=255, required=False)
    carbure_delivery_site_id = serializers.CharField(max_length=255, required=False)
    carbure_client_id = serializers.CharField(max_length=255, required=False)


class SplitSerializer(serializers.Serializer):
    payload = SplitCreateSerializer(many=True)

    def validate_payload(self, value):
        if not value:
            raise serializers.ValidationError("The payload field must not be empty.")

        if not isinstance(value, list):
            raise serializers.ValidationError("Parsed JSON is not a list")
        return value


class SplitMixin:
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
        request=SplitSerializer,
        responses=SplitResponseSerializer,
    )
    @action(methods=["post"], detail=False)
    def split(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")

        entity = get_object_or_404(Entity, id=entity_id)
        prefetched_data = get_prefetched_data(entity)
        serializer = SplitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data["payload"]

        new_lots = []
        for entry in payload:
            # check minimum fields
            required_fields = ["stock_id", "volume", "delivery_date"]
            for field in required_fields:
                if field not in entry:
                    raise ValidationError({"message": f"Missing field {field} in json object"})

            try:
                stock = CarbureStock.objects.get(carbure_id=entry["stock_id"])
            except Exception:
                raise ValidationError({"message": "Could not find stock"})

            if stock.carbure_client != entity:
                raise PermissionDenied({"message": "Stock does not belong to you"})

            try:
                volume = float(entry["volume"])
            except Exception:
                raise ValidationError({"message": "Could not parse volume"})

            # create child lot
            rounded_volume = round(volume, 2)
            lot = stock.get_parent_lot()
            lot.pk = None
            lot.transport_document_reference = None
            lot.carbure_client = None
            lot.unknown_client = None
            lot.carbure_delivery_site = None
            lot.unknown_delivery_site = None
            lot.delivery_site_country = None
            lot.lot_status = CarbureLot.DRAFT
            lot.delivery_type = CarbureLot.UNKNOWN
            lot.volume = rounded_volume
            lot.biofuel = stock.biofuel
            lot.weight = lot.get_weight()
            lot.lhv_amount = lot.get_lhv_amount()
            lot.parent_stock = stock
            lot.parent_lot = None

            # common, mandatory data
            lot.delivery_date = try_get_date(entry["delivery_date"])
            lot.year = lot.delivery_date.year
            lot.period = lot.delivery_date.year * 100 + lot.delivery_date.month
            lot.carbure_dispatch_site = stock.depot
            lot.dispatch_site_country = lot.carbure_dispatch_site.country if lot.carbure_dispatch_site else None
            lot.carbure_supplier_id = entity_id
            lot.supplier_certificate = entry.get("supplier_certificate", entity.default_certificate)
            lot.added_by_id = entity_id
            lot.dispatch_date = entry.get("dispatch_date", None)
            lot.unknown_client = entry.get("unknown_client", None)
            lot.unknown_delivery_site = entry.get("unknown_delivery_site", None)
            country_code = entry.get("delivery_site_country_id", None)
            if country_code is not None:
                try:
                    lot.delivery_site_country = Pays.objects.get(code_pays=country_code)
                except Exception:
                    lot.delivery_site_country = None
            lot.transport_document_type = entry.get("transport_document_type", CarbureLot.OTHER)
            lot.delivery_type = entry.get("delivery_type", CarbureLot.UNKNOWN)
            lot.transport_document_reference = entry.get("transport_document_reference", lot.delivery_type)
            delivery_site_id = entry.get("carbure_delivery_site_id", None)
            try:
                delivery_site = Depot.objects.get(customs_id=delivery_site_id)
                lot.carbure_delivery_site = delivery_site
                lot.delivery_site_country = delivery_site.country
            except Exception:
                pass
            try:
                lot.carbure_client = Entity.objects.get(id=entry.get("carbure_client_id", None))
            except Exception:
                lot.carbure_client = None

            if lot.delivery_type in [
                CarbureLot.BLENDING,
                CarbureLot.DIRECT,
                CarbureLot.PROCESSING,
            ]:
                if lot.transport_document_reference is None:
                    raise ValidationError(
                        {
                            "status": "error",
                            "message": "Missing transport_document_reference",
                        }
                    )
                if lot.carbure_client is None:
                    raise ValidationError({"status": "error", "message": "Mandatory carbure_client_id"})
                if lot.carbure_delivery_site is None:
                    raise ValidationError(
                        {
                            "status": "error",
                            "message": "Mandatory carbure_delivery_site",
                        }
                    )
            else:
                if lot.delivery_site_country is None:
                    raise ValidationError(
                        {
                            "status": "error",
                            "message": "Mandatory delivery_site_country",
                        }
                    )

            # check if the stock has enough volume and update it
            if rounded_volume > stock.remaining_volume:
                raise ValidationError(
                    {
                        "status": "error",
                        "message": "Not enough stock available Available [%.2f] Requested [%.2f]"
                        % (stock.remaining_volume, rounded_volume),
                    }
                )

            lot.save()
            new_lots.append(lot)
            stock.remaining_volume = round(stock.remaining_volume - rounded_volume, 2)
            stock.remaining_weight = stock.get_weight()
            stock.remaining_lhv_amount = stock.get_lhv_amount()
            stock.save()
            event = CarbureStockEvent()
            event.event_type = CarbureStockEvent.SPLIT
            event.stock = stock
            event.user = request.user
            event.metadata = {"message": "Envoi lot.", "volume_to_deduct": lot.volume}
            event.save()
            # create events
            e = CarbureLotEvent()
            e.event_type = CarbureLotEvent.CREATED
            e.lot = lot
            e.user = request.user
            e.save()
        background_bulk_sanity_checks(new_lots, prefetched_data)
        background_bulk_scoring(new_lots, prefetched_data)
        return Response({"status": "success", "data": [lot.id for lot in new_lots]})
