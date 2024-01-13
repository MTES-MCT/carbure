from datetime import date
from django import forms
from django.http import HttpRequest
from django.db import transaction
from django.views.decorators.http import require_POST
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.api.cpo.meter_readings.check_application import get_application_quarter
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.services.import_meter_reading_excel import import_meter_reading_excel


class AddMeterReadingApplicationForm(forms.Form):
    quarter = forms.IntegerField(required=False)
    year = forms.IntegerField(required=False)


class AddMeterReadingApplicationError:
    TOO_LATE = "TOO_LATE"
    MISSING_FILE = "MISSING_FILE"
    NO_READING_FOUND = "NO_READING_FOUND"
    VALIDATION_FAILED = "VALIDATION_FAILED"


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW], entity_type=[Entity.CPO])
def add_application(request: HttpRequest, entity: Entity):
    excel_file = request.FILES.get("file")

    if not excel_file:
        return ErrorResponse(400, AddMeterReadingApplicationError.MISSING_FILE)

    form = AddMeterReadingApplicationForm(request.POST)
    if not form.is_valid():
        return ErrorResponse(400, "MALFORMED_PARAMS", form.errors)

    # guess the application's quarter based on the current date
    # if it's in the last 10 days of a quarter, use this quarter
    # if it's in the first 20 days of a quarter, use the previous quarter
    auto_quarter, auto_year = get_application_quarter(date.today())
    quarter = form.cleaned_data["quarter"] or auto_quarter
    year = form.cleaned_data["year"] or auto_year

    if not quarter or not year:
        return ErrorResponse(400, AddMeterReadingApplicationError.TOO_LATE)

    existing_charge_points = ChargePointRepository.get_registered_charge_points(entity)
    meter_reading_data, errors = import_meter_reading_excel(excel_file, existing_charge_points)

    if len(meter_reading_data) == 0:
        return ErrorResponse(400, AddMeterReadingApplicationError.NO_READING_FOUND)

    if len(errors) > 0:
        return ErrorResponse(400, AddMeterReadingApplicationError.VALIDATION_FAILED)

    with transaction.atomic():
        replaced_applications = MeterReadingRepository.get_replaceable_applications(entity)

        # delete older pending applications
        replaced_applications.delete()

        application = ElecMeterReadingApplication(cpo=entity, quarter=quarter, year=year)
        meter_readings = [ElecMeterReading(**data, application=application, cpo=entity) for data in meter_reading_data]

        application.save()
        ElecMeterReading.objects.bulk_create(meter_readings)

    return SuccessResponse()
