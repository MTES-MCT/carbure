from django.http.response import JsonResponse
from core.decorators import check_user_rights
from core.helpers import (
    filter_lots,
    get_entity_lots_by_status,
)

from core.models import (
    CarbureLot,
    CarbureLotEvent,
    CarbureStock,
    CarbureStockEvent,
    Entity,
    UserRights,
)


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def lots_delete(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", None)
    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    filtered_lots = filter_lots(lots, request.POST, entity)
    if filtered_lots.count() == 0:
        return JsonResponse(
            {"status": "error", "message": "Could not find lots to delete"}, status=400
        )
    for lot in filtered_lots:
        if lot.added_by != entity:
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Entity not authorized to delete this lot",
                },
                status=403,
            )

        if lot.lot_status not in [CarbureLot.DRAFT, CarbureLot.REJECTED] and not (
            lot.lot_status in [CarbureLot.PENDING, CarbureLot.ACCEPTED]
            and lot.correction_status == CarbureLot.IN_CORRECTION
        ):
            # cannot delete lot accepted / frozen or already deleted
            return JsonResponse(
                {"status": "error", "message": "Cannot delete lot"}, status=400
            )

        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.DELETED
        event.lot = lot
        event.user = request.user
        event.save()
        lot.lot_status = CarbureLot.DELETED
        lot.save()
        if lot.parent_stock is not None:
            stock = CarbureStock.objects.get(
                id=lot.parent_stock.id
            )  # force refresh from db
            stock.remaining_volume = round(stock.remaining_volume + lot.volume, 2)
            stock.remaining_weight = stock.get_weight()
            stock.remaining_lhv_amount = stock.get_lhv_amount()
            stock.save()
            # save event
            event = CarbureStockEvent()
            event.event_type = CarbureStockEvent.UNSPLIT
            event.stock = lot.parent_stock
            event.user = request.user
            event.metadata = {
                "message": "child lot deleted. recredit volume.",
                "volume_to_credit": lot.volume,
            }
            event.save()
        if lot.parent_lot:
            if lot.parent_lot.delivery_type in [
                CarbureLot.PROCESSING,
                CarbureLot.TRADING,
            ]:
                lot.parent_lot.lot_status = CarbureLot.PENDING
                lot.parent_lot.delivery_type = CarbureLot.OTHER
                lot.parent_lot.save()
                # save event
                event = CarbureLotEvent()
                event.event_type = CarbureLotEvent.RECALLED
                event.lot = lot.parent_lot
                event.user = request.user
                event.metadata = {"message": "child lot deleted. back to inbox."}
                event.save()

    return JsonResponse({"status": "success"})
