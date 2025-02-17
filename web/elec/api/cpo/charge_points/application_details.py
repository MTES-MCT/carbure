from django import forms
from django.views.decorators.http import require_GET

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.models import Entity
from elec.api.cpo.charge_points.charge_points import annotate_with_latest_meter_reading_date
from elec.models import ElecChargePointApplication
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.serializers.elec_charge_point import ElecChargePointSerializer
from elec.services.export_charge_point_excel import export_charge_points_to_excel


class ApplicationDetailsForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ElecChargePointApplication.objects.all())


class ApplicationDetailsError:
    WRONG_APPLICATION = "WRONG_APPLICATION"
    WRONG_ENTITY = "WRONG_ENTITY"


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_application_details(request, entity):
    form = ApplicationDetailsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, ApplicationDetailsError.WRONG_APPLICATION, form.errors)

    application = form.cleaned_data["application_id"]

    if application.cpo != entity:
        return ErrorResponse(400, ApplicationDetailsError.WRONG_ENTITY)

    charge_points = ChargePointRepository.get_application_charge_points(application.cpo, application)
    charge_points = annotate_with_latest_meter_reading_date(charge_points)

    if "export" in request.GET:
        excel_file = export_charge_points_to_excel(charge_points, entity)
        return ExcelResponse(excel_file)

    serialized = ElecChargePointSerializer(charge_points, many=True).data
    return SuccessResponse(serialized)
