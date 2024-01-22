import traceback

from django import forms
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse

from core.decorators import check_admin_rights
from core.models import (
    CarbureLot,
)
from django.db.models import Case, Value, When

from core.utils import MultipleValueField


class AdminControlsLotsPinForm(forms.Form):
    selection = MultipleValueField(coerce=int, required=False)
    notify_auditor = forms.BooleanField(required=False)


@check_admin_rights()
def toggle_pin(request):
    form = AdminControlsLotsPinForm(request.POST)
    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    selection = form.cleaned_data["selection"]
    notify_auditor = form.cleaned_data["notify_auditor"]

    try:
        lots = CarbureLot.objects.filter(id__in=selection)
        lots.update(
            highlighted_by_admin=Case(
                When(highlighted_by_admin=True, then=Value(False)),
                When(highlighted_by_admin=False, then=Value(True)),
            )
        )
        if notify_auditor:
            lots.update(highlighted_by_auditor=True)
        return SuccessResponse()
    except:
        traceback.print_exc()
        return ErrorResponse(400, CarbureError.UNKNOWN_ERROR)
