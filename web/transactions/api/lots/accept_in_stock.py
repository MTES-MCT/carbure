from django.http.response import JsonResponse
from core.decorators import check_user_rights
from api.v4.helpers import (
    filter_lots,
    get_entity_lots_by_status,
)

from core.models import (
    CarbureLot,
    CarbureLotEvent,
    CarbureStock,
    Entity,
    UserRights,
)


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_in_stock(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    if entity.entity_type == Entity.OPERATOR:
        return JsonResponse(
            {"status": "error", "message": "Stock unavailable for Operators"},
            status=400,
        )

    for lot in lots.iterator():
        if entity != lot.carbure_client:
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
        lot.delivery_type = CarbureLot.STOCK
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
        stock = CarbureStock()
        stock.parent_lot = lot
        if lot.carbure_delivery_site is None:
            lot.lot_status = CarbureLot.PENDING
            lot.delivery_type = CarbureLot.UNKNOWN
            lot.save()
            return JsonResponse(
                {"status": "error", "message": "Cannot add stock for unknown Depot"},
                status=400,
            )
        stock.depot = lot.carbure_delivery_site
        stock.carbure_client = lot.carbure_client
        stock.remaining_volume = lot.volume
        stock.remaining_weight = lot.weight
        stock.remaining_lhv_amount = lot.lhv_amount
        stock.feedstock = lot.feedstock
        stock.biofuel = lot.biofuel
        stock.country_of_origin = lot.country_of_origin
        stock.carbure_production_site = lot.carbure_production_site
        stock.unknown_production_site = lot.unknown_production_site
        stock.production_country = lot.production_country
        stock.carbure_supplier = lot.carbure_supplier
        stock.unknown_supplier = lot.unknown_supplier
        stock.ghg_reduction = lot.ghg_reduction
        stock.ghg_reduction_red_ii = lot.ghg_reduction_red_ii
        stock.save()
        stock.carbure_id = "%sS%d" % (lot.carbure_id, stock.id)
        stock.save()
    return JsonResponse({"status": "success"})
