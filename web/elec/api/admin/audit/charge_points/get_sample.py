from django import forms
from django.views.decorators.http import require_GET
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.excel import ExcelResponse
from core.models import ExternalAdminRights
from elec.models.elec_charge_point import ElecChargePoint
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.serializers.elec_charge_point import ElecChargePointSampleSerializer
from elec.services.export_charge_point_excel import export_charge_points_sample_to_excel


class GetSampleError:
    NO_SAMPLE_FOUND = "NO_SAMPLE_FOUND"


class GetSampleForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ChargePointRepository.get_annotated_applications())
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

    audited_charge_points = audit_sample.audited_charge_points.all()
    charge_points = ElecChargePoint.objects.filter(charge_point_audit__in=audited_charge_points)

    if export:
        excel_file = export_charge_points_sample_to_excel(charge_points, application.cpo)
        return ExcelResponse(excel_file)

    return SuccessResponse(ElecChargePointSampleSerializer(charge_points, many=True).data)
