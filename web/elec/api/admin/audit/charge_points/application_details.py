from django import forms
from django.views.decorators.http import require_GET

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.excel import ExcelResponse
from core.models import ExternalAdminRights
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.serializers.elec_charge_point_application import ElecChargePointApplicationDetailsSerializer
from elec.services.export_charge_point_excel import export_charge_points_to_excel


class ApplicationDetailsForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ChargePointRepository.get_annotated_applications())
    export = forms.BooleanField(required=False)


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_application_details(request):
    form = ApplicationDetailsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application = form.cleaned_data["application_id"]
    export = form.cleaned_data["export"]

    if export:
        charge_points = ChargePointRepository.get_application_charge_points(application.cpo, application)
        excel_file = export_charge_points_to_excel(charge_points, application.cpo)
        return ExcelResponse(excel_file)

    charge_point_application = ElecChargePointApplicationDetailsSerializer(application).data
    return SuccessResponse(charge_point_application)
