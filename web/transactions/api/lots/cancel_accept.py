from core.common import (
    ErrorResponse,
    SuccessResponse,
)
from core.decorators import check_user_rights

from core.models import (
    CarbureLot,
    CarbureLotEvent,
    CarbureStock,
    CarbureStockTransformation,
    Entity,
    UserRights,
)


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def cancel_accept_lots(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_ids = request.POST.getlist("lot_ids", False)
    if not lot_ids:
        return ErrorResponse(400, CancelErrors.MISSING_LOT_IDS)

    entity = Entity.objects.get(pk=entity_id)
    lots = CarbureLot.objects.filter(pk__in=lot_ids)
    for lot in lots.iterator():
        if lot.carbure_client != entity:
            return ErrorResponse(403, CancelErrors.NOT_LOT_CLIENT)

        if lot.lot_status in (
            CarbureLot.DRAFT,
            CarbureLot.PENDING,
            CarbureLot.REJECTED,
            CarbureLot.FROZEN,
            CarbureLot.DELETED,
        ):
            return ErrorResponse(400, CancelErrors.WRONG_STATUS)

        # delete new lots created when the lot was accepted
        if lot.delivery_type in (CarbureLot.PROCESSING, CarbureLot.TRADING):
            children_lots = CarbureLot.objects.filter(parent_lot=lot).exclude(lot_status__in=[CarbureLot.DELETED])
            # do not do anything if the children lots are already used
            if children_lots.filter(lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN]).count() > 0:
                return ErrorResponse(400, CancelErrors.CHILDREN_IN_USE)
            else:
                children_lots.delete()

        # delete new stocks created when the lot was accepted
        if lot.delivery_type == CarbureLot.STOCK:
            children_stocks = CarbureStock.objects.filter(parent_lot=lot)
            children_stocks_children_lots = CarbureLot.objects.filter(parent_stock__in=children_stocks).exclude(
                lot_status=CarbureLot.DELETED
            )
            children_stocks_children_trans = CarbureStockTransformation.objects.filter(source_stock__in=children_stocks)
            # do not do anything if the children stocks are already used
            if children_stocks_children_lots.count() > 0 or children_stocks_children_trans.count() > 0:
                return ErrorResponse(400, CancelErrors.CHILDREN_IN_USE)
            else:
                children_stocks.delete()

        lot.lot_status = CarbureLot.PENDING
        lot.delivery_type = CarbureLot.UNKNOWN
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.CANCELLED
        event.lot = lot
        event.user = request.user
        event.save()
    return SuccessResponse()


class CancelErrors:
    MISSING_LOT_IDS = "MISSING_LOT_IDS"
    CANCEL_ACCEPT_NOT_ALLOWED = "CANCEL_ACCEPT_NOT_ALLOWED"
    NOT_LOT_CLIENT = "NOT_LOT_CLIENT"
    WRONG_STATUS = "WRONG_STATUS"
    CHILDREN_IN_USE = "CHILDREN_IN_USE"
