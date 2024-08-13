from django import forms
from django.views.decorators.http import require_GET
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.excel import ExcelResponse
from core.models import ExternalAdminRights
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.serializers.elec_audit_charge_point import ElecAuditChargePointSerializer
from elec.services.export_audited_charge_points_sample_to_excel import export_audited_charge_points_sample_to_excel


class GetSampleError:
    NO_SAMPLE_FOUND = "NO_SAMPLE_FOUND"


class GetSampleForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=MeterReadingRepository.get_annotated_applications())
    export = forms.BooleanField(required=False)


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_sample(request):
    form = GetSampleForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application = form.cleaned_data["application_id"]
    export = form.cleaned_data["export"]

    audit_sample = application.audit_sample.first()

    if not audit_sample:
        return ErrorResponse(404, GetSampleError.NO_SAMPLE_FOUND)

    audited_charge_points = audit_sample.audited_charge_points.all().select_related("charge_point")

    if export:
        excel_file = export_audited_charge_points_sample_to_excel(audited_charge_points, audit_sample.cpo)
        return ExcelResponse(excel_file)

    return SuccessResponse(ElecAuditChargePointSerializer(audited_charge_points, many=True).data)
