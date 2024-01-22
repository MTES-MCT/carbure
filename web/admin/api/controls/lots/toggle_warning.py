import traceback

from django import forms
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse

from core.decorators import check_admin_rights
from core.models import (
    GenericError,
)

from core.utils import MultipleValueField


class AdminControlsLotsToggleWarningForm(forms.Form):
    lot_id = forms.IntegerField()
    errors = MultipleValueField(coerce=str)
    checked = forms.BooleanField(required=False)


@check_admin_rights()
def toggle_warning(request):
    form = AdminControlsLotsToggleWarningForm(request.POST)
    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    lot_id = form.cleaned_data["lot_id"]
    errors = form.cleaned_data["errors"]
    checked = form.cleaned_data["checked"]

    try:
        for error in errors:
            try:
                lot_error = GenericError.objects.get(lot_id=lot_id, error=error)
            except:
                traceback.print_exc()
                return ErrorResponse(404, CarbureError.UNKNOWN_ERROR)
            lot_error.acked_by_admin = checked
            lot_error.save()
        return SuccessResponse()
    except:
        traceback.print_exc()
        return ErrorResponse(500, CarbureError.UNKNOWN_ERROR)
