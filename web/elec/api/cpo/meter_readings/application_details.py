from django import forms
from django.views.decorators.http import require_GET

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.models import Entity
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.services.create_meter_reading_excel import create_meter_readings_data, create_meter_readings_excel


class ApplicationDetailsForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ElecMeterReadingApplication.objects.all())


class ApplicationDetailsError:
    WRONG_APPLICATION = "WRONG_APPLICATION"
    WRONG_ENTITY = "WRONG_ENTITY"


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_application_details(request, entity: Entity):
    form = ApplicationDetailsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, ApplicationDetailsError.WRONG_APPLICATION, form.errors)

    application: ElecMeterReadingApplication = form.cleaned_data["application_id"]

    if application.cpo != entity:
        return ErrorResponse(400, ApplicationDetailsError.WRONG_ENTITY)

    charge_points = ChargePointRepository.get_registered_charge_points(entity)
    previous_application = MeterReadingRepository.get_previous_application(entity, application.quarter, application.year)
    meter_readings = MeterReadingRepository.get_application_meter_readings_summary(entity, application)

    meter_readings_data = create_meter_readings_data(charge_points, previous_application, meter_readings)

    if "export" in request.GET:
        file_name = f"meter_readings_{entity.slugify()}_Q{application.quarter}_{application.year}"
        excel_file = create_meter_readings_excel(
            file_name, application.quarter, application.year, meter_readings_data, extended=True
        )
        return ExcelResponse(excel_file)

    return SuccessResponse(meter_readings_data)
