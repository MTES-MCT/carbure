from django import forms
from django.views.decorators.http import require_GET
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.models import Entity
from elec.repositories.elec_audit_repository import ElecAuditRepository
from elec.serializers.elec_charge_point import ElecChargePointSampleSerializer
from elec.services.export_audited_charge_points_sample_to_excel import export_audited_charge_points_sample_to_excel


class GetSampleError:
    NO_SAMPLE_FOUND = "NO_SAMPLE_FOUND"


class GetSampleForm(forms.Form):
    audit_sample_id = forms.IntegerField()
    export = forms.BooleanField(required=False)


@require_GET
@check_user_rights(entity_type=[Entity.AUDITOR])
def get_sample(request):
    form = GetSampleForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    audit_sample_id = form.cleaned_data["audit_sample_id"]
    export = form.cleaned_data["export"]

    audit_sample = ElecAuditRepository.get_audited_sample_by_id(request.user, audit_sample_id)

    if not audit_sample:
        return ErrorResponse(404, GetSampleError.NO_SAMPLE_FOUND)

    audited_charge_points = audit_sample.audited_charge_points.all().select_related("charge_point")

    if export:
        excel_file = export_audited_charge_points_sample_to_excel(audited_charge_points, audit_sample.cpo)
        return ExcelResponse(excel_file)

    return SuccessResponse(ElecChargePointSampleSerializer(audited_charge_points, many=True).data)
