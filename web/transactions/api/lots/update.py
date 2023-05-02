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

    # query the database for all the traceability nodes related to these lots
    nodes = get_traceability_nodes([updated_lot])
    lot_node = nodes[0]

    # compute the lot quantity and check if it goes over the available stock if any
    quantity, is_over_stock_limit = get_lot_quantity(updated_lot, quantity_data)

    update = {**update_data, **quantity}

    try:
        # apply the update to the lot and check if the given entity can actually apply it
        lot_node.update(update, entity_id)
    except Exception as e:
        return ErrorResponse(400, UpdateLotError.FIELD_UPDATE_FORBIDDEN, {"message": str(e)})

    with transaction.atomic():
        lot_node.data.save()
        bulk_sanity_checks([updated_lot], prefetched_data)
        background_bulk_scoring([updated_lot], prefetched_data)

        if len(lot_node.diff) > 0:
            CarbureLotEvent.objects.create(
                event_type=CarbureLotEvent.UPDATED_BY_ADMIN,
                lot=lot_node.data,
                user=request.user,
                metadata=diff_to_metadata(lot_node.diff),
            )

        if is_over_stock_limit:
            GenericError.objects.create(
                lot=lot_node.data,
                field="quantity",
                error=CarbureStockErrors.NOT_ENOUGH_VOLUME_LEFT,
                display_to_creator=True,
            )

    return SuccessResponse()


def get_lot_quantity(lot, quantity_update):
    quantity = {}
    is_over_stock_limit = False

    if len(quantity_update) > 0:
        quantity = compute_lot_quantity(lot, quantity_update)

        # check that the new quantity can be extracted from a parent stock if any
        ancestor_stock = LotNode(lot).get_closest(LotNode.STOCK)

        if ancestor_stock:
            volume_before_update = lot.volume
            volume_change = round(quantity["volume"] - volume_before_update, 2)

            if volume_change > 0 and ancestor_stock.data.remaining_volume < volume_change:
                is_over_stock_limit = True
                quantity = compute_lot_quantity(lot, {"volume": volume_before_update})

    return quantity, is_over_stock_limit
