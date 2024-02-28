import traceback

from django import forms
from admin.api.controls.helpers import get_admin_summary_data
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.helpers import (
    filter_lots,
)
from core.decorators import check_admin_rights
from transactions.repositories.admin_lots_repository import TransactionsAdminLotsRepository


class AdminControlsLotsSummaryForm(forms.Form):
    status = forms.CharField()
    short = forms.BooleanField(required=False)


@check_admin_rights()
def get_lots_summary(request, entity):
    form = AdminControlsLotsSummaryForm(request.GET)
    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    status = form.cleaned_data["status"]
    short = form.cleaned_data["short"]

    try:
        lots = TransactionsAdminLotsRepository.get_admin_lots_by_status(entity, status)
        lots = filter_lots(lots, request.GET, entity, will_aggregate=True)
        summary = get_admin_summary_data(lots, short == "true")
        return SuccessResponse(summary)

    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CarbureError.UNKNOWN_ERROR)
