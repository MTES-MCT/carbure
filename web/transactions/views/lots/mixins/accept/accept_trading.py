from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.models import CarbureLot, CarbureLotEvent, Entity
from transactions.sanity_checks.helpers import get_prefetched_data


class AcceptTradingSerializer(serializers.Serializer):
    selection = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
    client_entity_id = serializers.CharField(required=False)
    unknown_client = serializers.CharField(required=False)
    certificate = serializers.CharField(required=False)


class AcceptTradingMixin:
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
        request=AcceptTradingSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False, url_path="accept-trading")
    def accept_trading(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")

        lots = self.filter_queryset(self.get_queryset())
        # TODO: fix, required ?
        serializer = AcceptTradingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selection = serializer.validated_data["selection"]
        client_entity_id = serializer.validated_data.get("client_entity_id")
        unknown_client = serializer.validated_data.get("unknown_client")
        certificate = serializer.validated_data.get("certificate")

        entity = Entity.objects.get(id=entity_id)

        if not client_entity_id and not unknown_client:
            raise ValidationError(
                {
                    "status": "error",
                    "message": "Please specify either client_entity_id or unknown_client",
                }
            )

        if not certificate and entity.default_certificate == "":
            raise ValidationError({"status": "error", "message": "Please specify a certificate"})

        if client_entity_id:
            try:
                client_entity = Entity.objects.get(pk=client_entity_id)
            except Exception:
                raise ValidationError({"status": "error", "message": "Could not find client entity"})
        else:
            client_entity = None

        if len(selection) > 0:
            lots = lots.filter(pk__in=selection)

        accepted_lot_ids = []
        transferred_lot_ids = []

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
            lot.delivery_type = CarbureLot.TRADING
            lot.save()

            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()

            # create child lot
            parent_lot_id = lot.id
            child_lot = lot
            child_lot.pk = None
            child_lot.carbure_client = client_entity
            child_lot.unknown_client = unknown_client
            child_lot.delivery_type = CarbureLot.UNKNOWN
            if child_lot.carbure_client is None:
                # auto-accept when the client is not registered in carbure
                child_lot.lot_status = CarbureLot.ACCEPTED
                child_lot.declared_by_client = True
            else:
                child_lot.declared_by_client = False
                child_lot.lot_status = CarbureLot.PENDING
            child_lot.correction_status = CarbureLot.NO_PROBLEMO
            child_lot.declared_by_supplier = False
            child_lot.added_by = entity
            child_lot.carbure_supplier = entity
            child_lot.supplier_certificate = certificate
            child_lot.unknown_supplier = None
            child_lot.parent_lot_id = parent_lot_id
            child_lot.parent_stock_id = None
            child_lot.save()
            transferred_lot_ids.append(child_lot.id)

            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.CREATED
            event.lot = child_lot
            event.user = request.user
            event.save()
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = child_lot
            event.user = request.user
            event.save()

        updated_lots = CarbureLot.objects.filter(id__in=accepted_lot_ids + transferred_lot_ids)
        prefetched_data = get_prefetched_data(entity)
        background_bulk_sanity_checks(updated_lots, prefetched_data)
        background_bulk_scoring(updated_lots, prefetched_data)
        return Response({"status": "success"})
