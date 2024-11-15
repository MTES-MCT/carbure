from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.models import CarbureLot, CarbureLotEvent


class AcceptBlendingSerializer(serializers.Serializer):
    selection = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)


class AcceptBlendingMixin:
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
        request=AcceptBlendingSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(
        methods=["post"],
        detail=False,
        url_path="accept-blending",
        serializer_class=AcceptBlendingSerializer,
    )
    def accept_blending(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")

        lots = self.filter_queryset(self.get_queryset())
        # TODO: fix, required ?
        serializer = AcceptBlendingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selection = serializer.validated_data["selection"]
        if len(selection) > 0:
            lots = lots.filter(pk__in=selection)

        for lot in lots:
            if int(entity_id) != lot.carbure_client_id:
                raise PermissionDenied({"message": "Only the client can accept the lot"})

            if lot.lot_status == CarbureLot.DRAFT:
                raise ValidationError({"message": "Cannot accept DRAFT"})
            elif lot.lot_status == CarbureLot.PENDING:
                # ok no problem
                pass
            elif lot.lot_status == CarbureLot.REJECTED:
                # the client changed his mind, ok
                pass
            elif lot.lot_status == CarbureLot.ACCEPTED:
                raise ValidationError({"message": "Lot already accepted."})
            elif lot.lot_status == CarbureLot.FROZEN:
                raise ValidationError({"message": "Lot is Frozen."})
            elif lot.lot_status == CarbureLot.DELETED:
                raise ValidationError({"message": "Lot is deleted."})

            lot.lot_status = CarbureLot.ACCEPTED
            lot.delivery_type = CarbureLot.BLENDING
            lot.save()
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()
        return Response({"status": "success"})
