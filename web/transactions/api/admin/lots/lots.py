import traceback

from django import forms

from core.carburetypes import CarbureError
from core.common import ErrorResponse
from core.decorators import check_admin_rights
from core.helpers import (
    get_lots_with_metadata,
)
from transactions.repositories.admin_lots_repository import TransactionsAdminLotsRepository


class AdminControlsLotsError:
    MISSING_STATUS = "MISSING_STATUS"


class AdminControlsLotsForm(forms.Form):
    status = forms.CharField(required=False)
    selection = forms.CharField(required=False)
    export = forms.BooleanField(required=False)


@check_admin_rights()
def get_lots(request, entity):
    form = AdminControlsLotsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    status = form.cleaned_data["status"]
    selection = form.cleaned_data["selection"]
    export = form.cleaned_data["export"]

    if not status and not selection:
        return ErrorResponse(400, AdminControlsLotsError.MISSING_STATUS)
    try:
        lots = TransactionsAdminLotsRepository.get_admin_lots_by_status(entity, status, export)
        return get_lots_with_metadata(lots, entity, request.GET)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CarbureError.UNKNOWN_ERROR)
