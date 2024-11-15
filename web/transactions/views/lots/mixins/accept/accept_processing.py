from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.models import CarbureLot, CarbureLotEvent, Entity


class AcceptProcessingSerializer(serializers.Serializer):
    selection = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
    processing_entity_id = serializers.IntegerField()


class AcceptProcessingMixin:
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
        request=AcceptProcessingSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False, url_path="accept-processing")
    def accept_processing(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")

        lots = self.filter_queryset(self.get_queryset())
        # TODO: fix, required ?
        serializer = AcceptProcessingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selection = serializer.validated_data["selection"]
        processing_entity_id = serializer.validated_data["processing_entity_id"]

        entity = Entity.objects.get(pk=entity_id)
        processing_entity = Entity.objects.get(pk=processing_entity_id)

        if len(selection) > 0:
            lots = lots.filter(pk__in=selection)
        accepted_lot_ids = []
        processed_lot_ids = []
        for lot in lots:
            if int(entity_id) != lot.carbure_client_id:
                raise PermissionDenied(
                    {
                        "message": "Only the client can accept the lot",
                    }
                )

            if lot.lot_status == CarbureLot.DRAFT:
                raise ValidationError({"status": "error", "message": "Cannot accept DRAFT"})
            elif lot.lot_status == CarbureLot.PENDING:
                # ok no problem
                pass
            elif lot.lot_status == CarbureLot.REJECTED:
                # the client changed his mind, ok
                pass
            elif lot.lot_status == CarbureLot.ACCEPTED:
                raise ValidationError({"status": "error", "message": "Lot already accepted."})
            elif lot.lot_status == CarbureLot.FROZEN:
                raise ValidationError({"status": "error", "message": "Lot is Frozen."})
            elif lot.lot_status == CarbureLot.DELETED:
                raise ValidationError({"status": "error", "message": "Lot is deleted."})

            lot.lot_status = CarbureLot.ACCEPTED
            lot.delivery_type = CarbureLot.PROCESSING
            lot.save()
            accepted_lot_ids.append(lot.id)

            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()

            # create child lot
            parent_lot_id = lot.id
            child_lot = lot
            child_lot.pk = None
            child_lot.carbure_client = processing_entity
            child_lot.delivery_type = CarbureLot.UNKNOWN
            child_lot.lot_status = CarbureLot.PENDING
            child_lot.correction_status = CarbureLot.NO_PROBLEMO
            child_lot.declared_by_supplier = False
            child_lot.declared_by_client = False
            child_lot.added_by = entity
            child_lot.carbure_supplier = entity
            child_lot.unknown_supplier = None
            child_lot.parent_lot_id = parent_lot_id
            child_lot.parent_stock_id = None
            child_lot.save()
            processed_lot_ids.append(child_lot.id)

            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.CREATED
            event.lot = child_lot
            event.user = request.user
            event.save()
        updated_lots = CarbureLot.objects.filter(id__in=accepted_lot_ids + processed_lot_ids)
        background_bulk_sanity_checks(updated_lots)
        background_bulk_scoring(updated_lots)

        return Response({"status": "success"})
