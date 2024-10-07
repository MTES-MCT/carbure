from datetime import date

from django import forms
from django.http import HttpRequest
from django.views.decorators.http import require_POST

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.models.elec_meter_reading import ElecMeterReading
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.services.import_meter_reading_excel import import_meter_reading_excel
from elec.services.meter_readings_application_quarter import get_application_quarter


class CheckMeterReadingApplicationForm(forms.Form):
    quarter = forms.IntegerField(required=False)
    year = forms.IntegerField(required=False)


class CheckMeterReadingApplicationError:
    TOO_LATE = "TOO_LATE"
    MISSING_FILE = "MISSING_FILE"
    NO_READING_FOUND = "NO_READING_FOUND"
    VALIDATION_FAILED = "VALIDATION_FAILED"


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW], entity_type=[Entity.CPO])
def check_application(request: HttpRequest, entity):
    excel_file = request.FILES.get("file")

    if not excel_file:
        return ErrorResponse(400, CheckMeterReadingApplicationError.MISSING_FILE)

    form = CheckMeterReadingApplicationForm(request.POST)
    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    # guess the application's quarter based on the current date
    # if it's in the last 10 days of a quarter, use this quarter
    # if it's in the first 20 days of a quarter, use the previous quarter
    auto_year, auto_quarter = get_application_quarter(date.today())
    quarter = form.cleaned_data["quarter"] or auto_quarter
    year = form.cleaned_data["year"] or auto_year

    charge_points = ChargePointRepository.get_registered_charge_points(entity)
    previous_application = MeterReadingRepository.get_previous_application(entity, quarter, year)
    renewable_share = MeterReadingRepository.get_renewable_share(year)
    previous_readings = ElecMeterReading.objects.filter(cpo=entity).select_related("meter", "meter__charge_point")

    meter_reading_data, errors, __ = import_meter_reading_excel(
        excel_file,
        charge_points,
        previous_readings,
        previous_application,
        renewable_share,
    )

    data = {}
    data["file_name"] = excel_file.name
    data["meter_reading_count"] = len(meter_reading_data)
    data["quarter"] = quarter
    data["year"] = year
    data["errors"] = []
    data["error_count"] = 0

    if len(errors) > 0:
        data["errors"] = errors
        data["error_count"] = len(data["errors"])
        return ErrorResponse(400, CheckMeterReadingApplicationError.VALIDATION_FAILED, data)

    if len(meter_reading_data) == 0:
        return ErrorResponse(400, CheckMeterReadingApplicationError.NO_READING_FOUND, data)

    return SuccessResponse(data)
