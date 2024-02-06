from django import forms
from django.views.decorators.http import require_GET
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.excel import ExcelResponse
from core.models import Entity, ExternalAdminRights
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.services.create_meter_reading_excel import create_meter_readings_data, create_meter_readings_excel


class ApplicationDetailsForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ElecMeterReadingApplication.objects.all())
    company_id = forms.ModelChoiceField(queryset=Entity.objects.filter(entity_type=Entity.CPO))


class ApplicationDetailsError:
    WRONG_APPLICATION = "WRONG_APPLICATION"
    WRONG_ENTITY = "WRONG_ENTITY"


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_application_details(request):
    form = ApplicationDetailsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, ApplicationDetailsError.WRONG_APPLICATION, form.errors)

    application: ElecMeterReadingApplication = form.cleaned_data["application_id"]
    company: Entity = form.cleaned_data["company_id"]

    charge_points = ChargePointRepository.get_registered_charge_points(company)
    previous_application = MeterReadingRepository.get_previous_application(company, application.quarter, application.year)
    meter_readings = MeterReadingRepository.get_application_meter_readings(company, application)

    meter_readings_data = create_meter_readings_data(charge_points, previous_application, meter_readings)

    if "export" in request.GET:
        file_name = f"meter_readings_{company.slugify()}_Q{application.quarter}_{application.year}"
        excel_file = create_meter_readings_excel(file_name, application.quarter, application.year, meter_readings_data, extended=True)  # fmt:skip
        return ExcelResponse(excel_file)

    return SuccessResponse(meter_readings_data)
