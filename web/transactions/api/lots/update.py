from django import forms

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from transactions.forms import LotForm
from transactions.helpers import compute_lot_quantity
from transactions.services.lots import LotUpdateFailure, do_update_lot


class UpdateLotError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    LOT_NOT_FOUND = "LOT_NOT_FOUND"
    FIELD_UPDATE_FORBIDDEN = "FIELD_UPDATE_FORBIDDEN"


class UpdateLotForm(forms.Form):
    entity_id = forms.IntegerField()
    lot_id = forms.ModelChoiceField(queryset=LotForm.LOTS)


def get_update_data(lot_to_update, lot_form):
    update_data, quantity_data = lot_form.get_lot_data()

    if len(quantity_data) > 0:
        biofuel = update_data.get("biofuel") or lot_to_update.biofuel
        update_data |= compute_lot_quantity(biofuel, quantity_data)

    return update_data


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def update_lot(request, *args, **kwargs):
    params_form = UpdateLotForm(request.POST)
    lot_form = LotForm(request.POST)
    user = request.user

    all_valid = params_form.is_valid() and lot_form.is_valid()
    if not all_valid:
        errors = params_form.errors | lot_form.errors
        return ErrorResponse(400, UpdateLotError.MALFORMED_PARAMS, errors)

    lot_to_update = params_form.cleaned_data["lot_id"]
    if not lot_to_update:
        return ErrorResponse(400, UpdateLotError.LOT_NOT_FOUND)

    entity_id = params_form.cleaned_data["entity_id"]
    entity = Entity.objects.get(pk=entity_id)
    update_data = get_update_data(lot_to_update, lot_form)

    try:
        do_update_lot(user, entity, lot_to_update, update_data)
    except LotUpdateFailure as f:
        return ErrorResponse(400, f.message, f.data)
    except Exception as e:
        return ErrorResponse(400, UpdateLotError.FIELD_UPDATE_FORBIDDEN, {"message": str(e)})

    return SuccessResponse()
