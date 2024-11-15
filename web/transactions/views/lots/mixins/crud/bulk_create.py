from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response

from carbure.tasks import background_bulk_scoring
from core.models import CarbureLotEvent, CarbureStockEvent, Entity
from core.serializers import GenericErrorSerializer
from transactions.helpers import bulk_insert_lots, construct_carbure_lot
from transactions.sanity_checks.helpers import get_prefetched_data

from .add import CreateLotSerializer


class BulkCreateResponseSerializer(serializers.Serializer):
    class EmbeddedGenericErrorSerializer(serializers.Serializer):
        index = serializers.IntegerField()
        errors = serializers.ListField(child=serializers.CharField(), allow_empty=True)

    lots = serializers.IntegerField()
    valid = serializers.IntegerField()
    invalid = serializers.IntegerField()
    errors = EmbeddedGenericErrorSerializer(many=True)


class BulkCreateMixin:
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
        request=CreateLotSerializer(many=True),
        responses=BulkCreateResponseSerializer,
    )
    @action(methods=["post"], detail=False, url_path="bulk-create")
    def bulk_create(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)

        d = get_prefetched_data(entity)
        lot_data_list = request.data
        if not isinstance(lot_data_list, list):
            raise ValidationError({"message": "Expected a list of lots."})

        uncreated_errors = []
        nb_total = 0
        nb_valid = 0
        nb_invalid = 0
        lots = []
        lots_errors = []
        with transaction.atomic():
            for index, lot_data in enumerate(lot_data_list):
                lot_obj, errors = construct_carbure_lot(d, entity, lot_data)
                if not lot_obj:
                    nb_invalid += 1
                    uncreated_errors.append(
                        {
                            "index": index,
                            "errors": GenericErrorSerializer(errors, many=True, read_only=True).data,
                        }
                    )
                else:
                    nb_valid += 1
                nb_total += 1
                lots.append(lot_obj)
                lots_errors.append(errors)

            lots_created = bulk_insert_lots(entity, lots, lots_errors, d)
            if len(lots_created) == 0:
                raise APIException({"message": "Something went wrong"})

            background_bulk_scoring(lots_created)
            for lot in lots_created:
                e = CarbureLotEvent()
                e.event_type = CarbureLotEvent.CREATED
                e.lot_id = lot.id
                e.user = request.user
                e.metadata = {"source": "API"}
                e.save()
                if lot.parent_stock:
                    event = CarbureStockEvent()
                    event.event_type = CarbureStockEvent.SPLIT
                    event.stock = lot.parent_stock
                    event.user = request.user
                    event.metadata = {
                        "message": "Envoi lot.",
                        "volume_to_deduct": lot.volume,
                    }
                    event.save()
        return Response(
            {
                "lots": nb_total,
                "valid": nb_valid,
                "invalid": nb_invalid,
                "errors": uncreated_errors,
            },
            status=status.HTTP_200_OK,
        )
