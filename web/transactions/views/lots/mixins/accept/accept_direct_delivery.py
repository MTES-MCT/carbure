from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.models import CarbureLot, CarbureLotEvent


class AcceptDirectDeliverySerializer(serializers.Serializer):
    selection = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)


class AcceptDirectDeliveryMixin:
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
        request=AcceptDirectDeliverySerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False, url_path="accept-direct-delivery")
    def accept_direct_delivery(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")

        lots = self.filter_queryset(self.get_queryset())
        # TODO: fix, required ?
        serializer = AcceptDirectDeliverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selection = serializer.validated_data["selection"]
        if len(selection) > 0:
            lots = lots.filter(pk__in=selection)

        for lot in lots:
            if int(entity_id) != lot.carbure_client_id:
                return PermissionDenied(
                    {
                        "message": "Only the client can accept the lot",
                    }
                )

            if lot.lot_status == CarbureLot.DRAFT:
                return ValidationError({"message": "Cannot accept DRAFT"}, status=400)

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
            lot.delivery_type = CarbureLot.DIRECT
            lot.save()
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()

        return Response({"status": "success"})
