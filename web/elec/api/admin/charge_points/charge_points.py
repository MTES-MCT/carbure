from django import forms
from django.views.decorators.http import require_GET

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.excel import ExcelResponse
from core.models import Entity, ExternalAdminRights
from elec.api.cpo.charge_points.charge_points import annotate_with_latest_meter_reading_date
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.serializers.elec_charge_point import ElecChargePointSerializer
from elec.services.export_charge_point_excel import export_charge_points_to_excel


class ChargePointsForm(forms.Form):
    company_id = forms.ModelChoiceField(queryset=Entity.objects.filter(entity_type=Entity.CPO))


class ChargePointsError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_charge_points(request, entity):
    form = ChargePointsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, ChargePointsError.MALFORMED_PARAMS, form.errors)

    company = form.cleaned_data["company_id"]
    charge_points = ChargePointRepository.get_cpo_charge_points(company)
    charge_points = annotate_with_latest_meter_reading_date(charge_points)

    if "export" in request.GET:
        excel_file = export_charge_points_to_excel(charge_points, entity)
        return ExcelResponse(excel_file)

    serialized = ElecChargePointSerializer(charge_points, many=True).data
    return SuccessResponse(serialized)
