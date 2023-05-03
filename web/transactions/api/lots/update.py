from django.db import transaction
from django import forms

from carbure.tasks import background_bulk_scoring
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from core.carburetypes import CarbureStockErrors
from core.models import UserRights, CarbureLotEvent, Entity, GenericError
from core.traceability import LotNode, get_traceability_nodes, diff_to_metadata
from api.v4.lots import compute_lot_quantity
from api.v4.sanity_checks import get_prefetched_data, bulk_sanity_checks
from transactions.forms import LotForm


class UpdateLotError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    MISSING_LOT_ID = "MISSING_LOT_ID"
    LOT_NOT_FOUND = "LOT_NOT_FOUND"
    LOT_UPDATE_FAILED = "LOT_UPDATE_FAILED"
    FIELD_UPDATE_FORBIDDEN = "FIELD_UPDATE_FORBIDDEN"
    INTEGRITY_ERROR = "INTEGRITY_ERROR"


class UpdateLotForm(forms.Form):
    entity_id = forms.IntegerField()
    lot_id = forms.ModelChoiceField(queryset=LotForm.LOTS)


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def update_lot(request, *args, **kwargs):
    params_form = UpdateLotForm(request.POST)
    lot_form = LotForm(request.POST)

    if not params_form.is_valid() or not lot_form.is_valid():
        return ErrorResponse(400, UpdateLotError.MALFORMED_PARAMS, {**params_form.errors, **lot_form.errors})

    entity_id = params_form.cleaned_data["entity_id"]
    updated_lot = params_form.cleaned_data["lot_id"]

    entity = Entity.objects.get(pk=entity_id)

    if not updated_lot or updated_lot.added_by != entity:
        return ErrorResponse(400, UpdateLotError.LOT_NOT_FOUND)

    prefetched_data = get_prefetched_data(entity)

    # convert the form data to a dict that can be applied as lot update
    update_data, quantity_data = lot_form.get_lot_data()

    update = {**update_data}
    if len(quantity_data) > 0:
        quantity = compute_lot_quantity(updated_lot, quantity_data)
        update = {**update_data, **quantity}

    # query the database for all the traceability nodes related to these lots
    nodes = get_traceability_nodes([updated_lot])
    lot_node = nodes[0]

    stock_update, stock_error = enforce_stock_integrity(lot_node, update)

    if stock_update is not None:
        update.update(stock_update)

    try:
        # apply the update to the lot and check if the given entity can actually apply it
        lot_node.update(update, entity_id)
        lot_node.data.update_ghg()
    except Exception as e:
        return ErrorResponse(400, UpdateLotError.FIELD_UPDATE_FORBIDDEN, {"message": str(e)})

    with transaction.atomic():
        lot_node.data.save()

        bulk_sanity_checks([lot_node.data], prefetched_data)
        background_bulk_scoring([lot_node.data], prefetched_data)

        if stock_error is not None:
            stock_error.save()

        if len(lot_node.diff) > 0:
            CarbureLotEvent.objects.create(
                event_type=CarbureLotEvent.UPDATED,
                lot=lot_node.data,
                user=request.user,
                metadata=diff_to_metadata(lot_node.diff),
            )

    return SuccessResponse()


# before applying an update, check that if the lot comes from a stock
# the stock has enough volume left to allow the update
def enforce_stock_integrity(lot_node: LotNode, update: dict):
    ancestor_stock_node = lot_node.get_closest(LotNode.STOCK)

    if ancestor_stock_node is None:
        return None, None

    ancestor_stock = ancestor_stock_node.data
    volume_before_update = lot_node.data.volume
    volume_change = round(update["volume"] - volume_before_update, 2)

    # if the volume is above the allowed limit, reset it and create an error to explain why
    if volume_change > 0 and ancestor_stock.remaining_volume < volume_change:
        reset_quantity = compute_lot_quantity(lot_node.data, {"volume": volume_before_update})
        error = GenericError(
            lot=lot_node.data,
            field="quantity",
            error=CarbureStockErrors.NOT_ENOUGH_VOLUME_LEFT,
            display_to_creator=True,
        )
        return reset_quantity, error

    # otherwise, update the parent stock volume to match the new reality
    ancestor_stock.remaining_volume = round(ancestor_stock.remaining_volume - volume_change, 2)
    ancestor_stock.remaining_weight = ancestor_stock.get_weight()
    ancestor_stock.remaining_lhv_amount = ancestor_stock.get_lhv_amount()
    ancestor_stock.save()

    return None, None
