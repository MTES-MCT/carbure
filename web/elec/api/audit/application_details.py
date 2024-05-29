from django import forms
from django.views.decorators.http import require_GET
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.models import Entity
from elec.repositories.elec_audit_repository import ElecAuditRepository
from elec.serializers.elec_audit_sample_serializer import ElecAuditSampleDetailsSerializer
from elec.services.export_charge_point_excel import export_charge_points_to_excel


class ApplicationDetailsForm(forms.Form):
    application_id = forms.IntegerField()
    export = forms.BooleanField(required=False)


@require_GET
@check_user_rights(entity_type=[Entity.AUDITOR])
def get_application_details(request):
    form = ApplicationDetailsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application_id = form.cleaned_data["application_id"]

    audit_sample = ElecAuditRepository.get_audited_application_by_id(request.user, application_id)

    charge_point_application = ElecAuditSampleDetailsSerializer(audit_sample).data
    return SuccessResponse(charge_point_application)
