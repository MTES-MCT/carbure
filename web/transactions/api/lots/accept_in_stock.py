from django.db import transaction

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.helpers import filter_lots, get_entity_lots_by_status
from core.models import CarbureLot, CarbureLotEvent, CarbureStock, Entity, UserRights


class AcceptStockError:
    STOCK_CREATION_FAILED = "STOCK_CREATION_FAILED"


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_in_stock(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    errors = {}

    updated_lots = []
    created_events = []
    created_stocks = []

    for lot in lots:
        lot_errors = []

        if entity != lot.carbure_client:
            lot_errors.push("Only the client can accept the lot")

        if lot.lot_status == CarbureLot.DRAFT:
            lot_errors.push("Cannot accept drafts.")
        elif lot.lot_status == CarbureLot.PENDING:
            pass  # ok no problem
        elif lot.lot_status == CarbureLot.REJECTED:
            pass  # the client changed his mind, ok
        elif lot.lot_status == CarbureLot.ACCEPTED:
            lot_errors.push("Lot is already accepted.")
        elif lot.lot_status == CarbureLot.FROZEN:
            lot_errors.push("Lot is frozen.")
        elif lot.lot_status == CarbureLot.DELETED:
            lot_errors.push("Lot is deleted.")

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.STOCK

        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user

        if lot.carbure_delivery_site is None:
            lot.lot_status = CarbureLot.PENDING
            lot.delivery_type = CarbureLot.UNKNOWN
            lot_errors.push("Cannot add stock for unknown Depot")

        stock = CarbureStock()
        stock.parent_lot = lot
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

        if len(lot_errors) > 0:
            errors[lot.id] = lot_errors
        else:
            updated_lots.append(lot)
            created_events.append(event)
            created_stocks.append(stock)

    if len(errors) > 0:
        return ErrorResponse(400, AcceptStockError.STOCK_CREATION_FAILED, errors)

    with transaction.atomic():
        CarbureLot.objects.bulk_update(updated_lots, ["lot_status", "delivery_type"])
        CarbureLotEvent.objects.bulk_create(created_events)
        bulk_create_stocks(created_stocks)

    return SuccessResponse()


@transaction.atomic()
def bulk_create_stocks(stocks):
    # create the stock rows, then generate carbure_id for all of them
    CarbureStock.objects.bulk_create(stocks)
    new_stocks = CarbureStock.objects.order_by("-id")[0 : len(stocks)]
    [stock.generate_carbure_id() for stock in new_stocks]
    CarbureStock.objects.bulk_update(new_stocks, ["carbure_id"])
    return new_stocks
