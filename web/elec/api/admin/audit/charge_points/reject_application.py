from django import forms
from django.http import HttpRequest

from django.views.decorators.http import require_POST
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from elec.models.elec_charge_point_application import ElecChargePointApplication


class RejectApplicationForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ElecChargePointApplication.objects.all())
    force_rejection = forms.BooleanField(required=False)


class RejectApplicationError:
    AUDIT_NOT_STARTED = "AUDIT_NOT_STARTED"
    ALREADY_CHECKED = "ALREADY_CHECKED"


@require_POST
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def reject_application(request: HttpRequest):
    form = RejectApplicationForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application = form.cleaned_data["application_id"]
    force_rejection = form.cleaned_data["force_rejection"]

    if application.status in (ElecChargePointApplication.ACCEPTED, ElecChargePointApplication.REJECTED):
        return ErrorResponse(400, RejectApplicationError.ALREADY_CHECKED, "Application has already been checked by admin")

    if application.status == ElecChargePointApplication.PENDING and not force_rejection:
        return ErrorResponse(
            400, RejectApplicationError.AUDIT_NOT_STARTED, "Application cannot be rejected if audit is not started"
        )

    application.status = ElecChargePointApplication.REJECTED
    application.save()

    return SuccessResponse()
