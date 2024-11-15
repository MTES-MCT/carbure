from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.models import CarbureLot, CarbureLotEvent, Entity
from core.notifications import notify_lots_rejected


class RejectMixin:
    @extend_schema(
        filters=True,
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["get"], detail=False)
    def reject(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)

        mutable_params = request.GET.copy()
        mutable_params["will_aggregate"] = "true"
        request.GET = mutable_params

        lots = self.filter_queryset(self.get_queryset())

        for lot in lots:
            if lot.carbure_client != entity:
                raise PermissionDenied(
                    {
                        "message": "Only the client can reject this lot",
                    }
                )

            if lot.lot_status == CarbureLot.DRAFT:
                raise ValidationError({"status": "error", "message": "Cannot reject DRAFT"})
            elif lot.lot_status == CarbureLot.PENDING:
                pass
            elif lot.lot_status == CarbureLot.REJECTED:
                raise ValidationError({"status": "error", "message": "Lot is already rejected."})
            elif lot.lot_status == CarbureLot.ACCEPTED:
                pass
            elif lot.lot_status == CarbureLot.FROZEN:
                raise ValidationError({"message": "Lot is Frozen. Cannot reject. Please invalidate declaration first."})
            elif lot.lot_status == CarbureLot.DELETED:
                raise ValidationError({"message": "Lot is deleted. Cannot reject"})

            lot.lot_status = CarbureLot.REJECTED
            lot.correction_status = CarbureLot.IN_CORRECTION
            lot.carbure_client = None
            lot.save()
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.REJECTED
            event.lot = lot
            event.user = request.user
            event.save()
        notify_lots_rejected(lots)
        return Response({"status": "success"})
