from django.http.response import JsonResponse
from core.decorators import check_user_rights
from core.helpers import (
    filter_lots,
    get_entity_lots_by_status,
)

from core.models import (
    CarbureLot,
    CarbureLotEvent,
    Entity,
    UserRights,
)


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_direct_delivery(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Only the client can accept the lot",
                },
                status=403,
            )

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse(
                {"status": "error", "message": "Cannot accept DRAFT"}, status=400
            )
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse(
                {"status": "error", "message": "Lot already accepted."}, status=400
            )
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {"status": "error", "message": "Lot is Frozen."}, status=400
            )
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse(
                {"status": "error", "message": "Lot is deleted."}, status=400
            )

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.DIRECT
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
    return JsonResponse({"status": "success"})
