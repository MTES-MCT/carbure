from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.models import CarbureLot, CarbureLotEvent


class AcceptBlendingMixin:
    @action(methods=["post"], detail=False, url_path="accept-blending")
    def accept_blending(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")

        lots = self.filter_queryset(self.get_queryset())
        # TODO: fix, required ?
        selection = request.data.getlist("selection")

        if len(selection) > 0:
            lots = lots.filter(pk__in=selection)

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
            lot.delivery_type = CarbureLot.BLENDING
            lot.save()
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()
        return Response({"status": "success"})
