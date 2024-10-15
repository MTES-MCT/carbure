from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apikey.authentication import APIKeyAuthentication
from carbure.tasks import background_bulk_scoring
from core.models import CarbureLotEvent, Entity
from core.serializers import CarbureLotPublicSerializer
from transactions.helpers import bulk_insert_lots, construct_carbure_lot
from transactions.sanity_checks.helpers import get_prefetched_data


class CreateLotSerializer(serializers.Serializer):
    """
    free_field, null
    carbure_stock_id, null,
    delivery_date, null
    biofuel_code, null,
    feedstock_code, null
    country_code, null
    production_site_certificate, null
    production_site_certificate_type, null
    carbure_production_site, null
    unknown_producer,
    unknown_production_site,
    production_country_code,
    production_site_commissioning_date,
    production_site_double_counting_certificate
    eec,
    el,
    ep,
    etd,
    eu,
    esca,
    eccs,
    eccr,
    eee,

    delivery_type,
    carbure_client_id,
    unknown_client,

    quantity
    unit
    volume,
    weight,
    lhv_amount,

    unknown_supplier,
    supplier_certificate,

    transport_document_type
    transport_document_reference,
    carbure_delivery_site_depot_id,
    unknown_delivery_site,
    delivery_site_country_code,

    vendor_certificate,
    """


class AddLotError:
    LOT_CREATION_FAILED = ("LOT_CREATION_FAILED", _("Le lot n'a pas pu être créé."))


class AddMixin:
    @action(
        methods=["post"],
        detail=False,
        authentication_classes=(SessionAuthentication, BasicAuthentication, APIKeyAuthentication),
    )
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
