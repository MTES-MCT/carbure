from django import forms
from django.http import HttpRequest

from django.views.decorators.http import require_POST
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import Entity, ExternalAdminRights
from elec.models.elec_charge_point_application import ElecChargePointApplication


class AcceptApplicationForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ElecChargePointApplication.objects.all())
    company_id = forms.ModelChoiceField(queryset=Entity.objects.filter(entity_type=Entity.CPO))


class AcceptApplicationError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    WRONG_ENTITY = "WRONG_ENTITY"


@require_POST
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def accept_application(request: HttpRequest):
    form = AcceptApplicationForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, AcceptApplicationError.MALFORMED_PARAMS, form.errors)

    application = form.cleaned_data["application_id"]
    company = form.cleaned_data["company_id"]

    if application.cpo != company:
        return ErrorResponse(400, AcceptApplicationError.WRONG_ENTITY)

    application.status = ElecChargePointApplication.ACCEPTED
    application.save()

    return SuccessResponse()
