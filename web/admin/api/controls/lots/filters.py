from django import forms
from admin.helpers import get_admin_lots_by_status
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.helpers import (
    get_lots_filters_data,
)
from core.decorators import check_admin_rights
from transactions.repositories.admin_lots_repository import TransactionsAdminLotsRepository


class AdminControlsLotsFiltersForm(forms.Form):
    status = forms.CharField()
    field = forms.CharField()


@check_admin_rights()
def get_lots_filters(request, entity):
    form = AdminControlsLotsFiltersForm(request.GET)
    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    status = form.cleaned_data["status"]
    field = form.cleaned_data["field"]

    lots = TransactionsAdminLotsRepository.get_admin_lots_by_status(entity, status)
    data = get_lots_filters_data(lots, request.GET, entity, field)

    if data is None:
        return ErrorResponse(400, CarbureError.UNKNOWN_ERROR)
    else:
        return SuccessResponse(data)
