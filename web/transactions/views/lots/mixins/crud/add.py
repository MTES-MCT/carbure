from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from carbure.tasks import background_bulk_scoring
from core.models import CarbureLotEvent, Entity
from core.serializers import CarbureLotPublicSerializer
from transactions.helpers import bulk_insert_lots, construct_carbure_lot
from transactions.sanity_checks.helpers import get_prefetched_data


class CreateLotSerializer(serializers.Serializer):
    free_field = serializers.CharField(allow_null=True, required=False)
    carbure_stock_id = serializers.CharField(allow_null=True, required=False)
    delivery_date = serializers.DateField(allow_null=True, required=False)
    biofuel_code = serializers.CharField(allow_null=True, required=False)
    feedstock_code = serializers.CharField(allow_null=True, required=False)
    country_code = serializers.CharField(allow_null=True, required=False)
    production_site_certificate = serializers.CharField(allow_null=True, required=False)
    production_site_certificate_type = serializers.CharField(allow_null=True, required=False)
    carbure_production_site = serializers.CharField(allow_null=True, required=False)
    unknown_producer = serializers.CharField(required=False)
    unknown_production_site = serializers.CharField(required=False)
    production_country_code = serializers.CharField(allow_null=True, required=False)
    production_site_commissioning_date = serializers.DateField(allow_null=True, required=False)
    production_site_double_counting_certificate = serializers.CharField(allow_null=True, required=False)

    # GHG emission values
    eec = serializers.FloatField(allow_null=True, required=False)
    el = serializers.FloatField(allow_null=True, required=False)
    ep = serializers.FloatField(allow_null=True, required=False)
    etd = serializers.FloatField(allow_null=True, required=False)
    eu = serializers.FloatField(allow_null=True, required=False)
    esca = serializers.FloatField(allow_null=True, required=False)
    eccs = serializers.FloatField(allow_null=True, required=False)
    eccr = serializers.FloatField(allow_null=True, required=False)
    eee = serializers.FloatField(allow_null=True, required=False)

    # Delivery information
    delivery_type = serializers.CharField(allow_null=True, required=False)
    carbure_client_id = serializers.IntegerField(allow_null=True, required=False)
    unknown_client = serializers.CharField(required=False)

    # Quantity information
    quantity = serializers.FloatField(allow_null=True, required=False)
    unit = serializers.CharField(allow_null=True, required=False)
    volume = serializers.FloatField(allow_null=True, required=False)
    weight = serializers.FloatField(allow_null=True, required=False)
    lhv_amount = serializers.FloatField(allow_null=True, required=False)

    # Supplier information
    unknown_supplier = serializers.CharField(required=False)
    supplier_certificate = serializers.CharField(allow_null=True, required=False)

    # Transport document
    transport_document_type = serializers.CharField(allow_null=True, required=False)
    transport_document_reference = serializers.CharField(allow_null=True, required=False)
    carbure_delivery_site_depot_id = serializers.IntegerField(allow_null=True, required=False)
    unknown_delivery_site = serializers.CharField(required=False)
    delivery_site_country_code = serializers.CharField(allow_null=True, required=False)

    # Vendor certificate
    vendor_certificate = serializers.CharField(allow_null=True, required=False)


class AddLotError:
    LOT_CREATION_FAILED = ("LOT_CREATION_FAILED", _("Le lot n'a pas pu être créé."))


class AddMixin:
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
        request=CreateLotSerializer,
        responses=CarbureLotPublicSerializer,
    )
    @action(methods=["post"], detail=False)
    def add(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)

        d = get_prefetched_data(entity)
        lot_data = request.data
        lot, errors = construct_carbure_lot(d, entity, lot_data)
        if not lot:
            raise ValidationError({"message": AddLotError.LOT_CREATION_FAILED})

        # run sanity checks, insert lot and errors
        with transaction.atomic():
            lots_created = bulk_insert_lots(entity, [lot], [errors], d)

            if len(lots_created) == 0:
                raise ValidationError({"message": AddLotError.LOT_CREATION_FAILED})

            background_bulk_scoring(lots_created)

            CarbureLotEvent.objects.create(
                event_type=CarbureLotEvent.CREATED,
                lot_id=lots_created[0].id,
                user=request.user,
                metadata={"source": "MANUAL"},
            )

        data = CarbureLotPublicSerializer(lots_created[0]).data
        return Response(data)
