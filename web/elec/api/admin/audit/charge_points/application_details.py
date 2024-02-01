import datetime
from math import e
from django import forms
from django.views.decorators.http import require_GET
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.excel import ExcelResponse
from core.models import Entity, ExternalAdminRights
from elec.api.cpo.charge_points import application_details
from elec.models import ElecChargePoint
from elec.models import ElecChargePointApplication
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.serializers.elec_charge_point import ElecChargePointSerializer
from elec.serializers.elec_charge_point_application import ElecChargePointApplicationSerializer
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
        charge_points = ElecChargePoint.objects.filter(application=application.id)
        excel_file = export_charge_points_to_excel(charge_points, application.cpo)
        return ExcelResponse(excel_file)

    return SuccessResponse(ElecChargePointApplicationSerializer(application).data)
