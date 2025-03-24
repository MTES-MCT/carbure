from datetime import timedelta

from django import forms
from django.views.decorators.http import require_GET

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.models import Entity
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.services.create_meter_reading_excel import create_meter_readings_excel
from elec.services.meter_readings_application_quarter import last_day_of_quarter


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

    end_of_quarter = last_day_of_quarter(application.year, application.quarter) + timedelta(days=15)

    charge_points = MeterReadingRepository.get_application_charge_points(entity, application)
    charge_points = MeterReadingRepository.annotate_charge_points_with_latest_readings(charge_points, end_of_quarter)

    meter_reading_data = []
    for charge_point in charge_points:
        meter_reading_data.append(
            {
                "charge_point_id": charge_point.charge_point_id,
                "previous_reading": charge_point.second_latest_reading_index,
                "current_reading": charge_point.latest_reading_index,
                "reading_date": charge_point.latest_reading_date,
            }
        )

    if "export" in request.GET:
        file_name = f"meter_readings_{entity.slugify()}_Q{application.quarter}_{application.year}"
        excel_file = create_meter_readings_excel(
            file_name, application.quarter, application.year, meter_reading_data, extended=True
        )
        return ExcelResponse(excel_file)

    return SuccessResponse(meter_reading_data)
