import datetime
from django import forms
from django.views.decorators.http import require_GET
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.excel import ExcelResponse
from core.models import Entity, ExternalAdminRights
from elec.models import ElecChargePoint
from elec.models import ElecChargePointApplication
from elec.serializers.elec_charge_point import ElecChargePointSerializer
from elec.services.export_charge_point_excel import export_charge_points_to_excel


class ApplicationDetailsForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ElecChargePointApplication.objects.all())
    company_id = forms.ModelChoiceField(queryset=Entity.objects.filter(entity_type=Entity.CPO))


class ApplicationDetailsError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    WRONG_ENTITY = "WRONG_ENTITY"


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_application_details(request):
    form = ApplicationDetailsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, ApplicationDetailsError.MALFORMED_PARAMS, form.errors)

    application = form.cleaned_data["application_id"]
    company = form.cleaned_data["company_id"]

    if application.cpo != company:
        return ErrorResponse(400, ApplicationDetailsError.WRONG_ENTITY)

    charge_points = ElecChargePoint.objects.filter(cpo=company, application=application)

    if "export" in request.GET:
        excel_file = export_charge_points_to_excel(charge_points, company)
        return ExcelResponse(excel_file)

    serialized = ElecChargePointSerializer(charge_points, many=True).data
    return SuccessResponse(serialized)
