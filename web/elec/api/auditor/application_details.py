from django import forms
from django.views.decorators.http import require_GET

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.repositories.elec_audit_repository import ElecAuditRepository
from elec.serializers.elec_audit_sample import ElecAuditSampleDetailsSerializer


class ApplicationDetailsForm(forms.Form):
    audit_sample_id = forms.IntegerField()
    export = forms.BooleanField(required=False)


@require_GET
@check_user_rights(entity_type=[Entity.AUDITOR])
def get_application_details(request):
    form = ApplicationDetailsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    audit_sample_id = form.cleaned_data["audit_sample_id"]

    audit_sample = ElecAuditRepository.get_audited_sample_by_id(request.user, audit_sample_id)

    charge_point_application = ElecAuditSampleDetailsSerializer(audit_sample).data
    return SuccessResponse(charge_point_application)
