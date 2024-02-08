from django import forms
from django.http import HttpRequest

from django.views.decorators.http import require_POST
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication


class AcceptApplicationForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ElecMeterReadingApplication.objects.all())


@require_POST
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def start_audit(request: HttpRequest):
    form = AcceptApplicationForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application = form.cleaned_data["application_id"]

    application.status = ElecMeterReadingApplication.AUDIT_IN_PROGRESS
    application.save()

    return SuccessResponse()
