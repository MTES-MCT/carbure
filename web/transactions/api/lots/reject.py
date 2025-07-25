from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.helpers import filter_lots, get_entity_lots_by_status
from core.models import (
    CarbureLot,
    CarbureLotEvent,
    Entity,
    UserRights,
)
from core.notifications import notify_lots_rejected


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def reject_lot(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots:
        if lot.carbure_client != entity:
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Only the client can reject this lot",
                },
                status=403,
            )

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({"status": "error", "message": "Cannot reject DRAFT"}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            return JsonResponse({"status": "error", "message": "Lot is already rejected."}, status=400)
        elif lot.lot_status == CarbureLot.ACCEPTED:
            pass
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Lot is Frozen. Cannot reject. Please invalidate declaration first.",
                },
                status=400,
            )
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse(
                {"status": "error", "message": "Lot is deleted. Cannot reject"},
                status=400,
            )

        lot.lot_status = CarbureLot.REJECTED
        lot.correction_status = CarbureLot.IN_CORRECTION
        lot.carbure_client = None
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.REJECTED
        event.lot = lot
        event.user = request.user
        event.entity = entity
        event.save()
    notify_lots_rejected(lots)
    return JsonResponse({"status": "success"})
