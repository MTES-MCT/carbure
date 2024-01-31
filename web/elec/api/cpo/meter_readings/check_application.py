from datetime import date, timedelta
from django import forms
from django.http import HttpRequest
from django.views.decorators.http import require_POST
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.services.import_meter_reading_excel import import_meter_reading_excel


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
    auto_quarter, auto_year = get_application_quarter(date.today())
    quarter = form.cleaned_data["quarter"] or auto_quarter
    year = form.cleaned_data["year"] or auto_year

    if not quarter or not year:
        return ErrorResponse(400, CheckMeterReadingApplicationError.TOO_LATE)

    existing_charge_points = ChargePointRepository.get_registered_charge_points(entity)

    meter_reading_data, errors = import_meter_reading_excel(excel_file, existing_charge_points)
    pending_application_already_exists = MeterReadingRepository.get_replaceable_applications(entity).count() > 0

    if len(meter_reading_data) == 0:
        return ErrorResponse(400, CheckMeterReadingApplicationError.NO_READING_FOUND)

    data = {}
    data["file_name"] = excel_file.name
    data["meter_reading_count"] = len(meter_reading_data)
    data["quarter"] = quarter
    data["year"] = year
    data["errors"] = []
    data["error_count"] = 0
    data["pending_application_already_exists"] = pending_application_already_exists

    if len(errors) > 0:
        data["errors"] = errors
        data["error_count"] = len(data["errors"])
        return ErrorResponse(400, CheckMeterReadingApplicationError.VALIDATION_FAILED, data)

    return SuccessResponse(data)


def get_application_quarter(reference_date: date):
    quarter = (reference_date.month - 1) // 3 + 1
    first_day_of_quarter = date(reference_date.year, (quarter - 1) * 3 + 1, 1)
    last_day_of_quarter = (first_day_of_quarter + timedelta(days=3 * 31)).replace(day=1) - timedelta(days=1)

    # special condition to ignore TOO_LATE error for the first ever round of applications
    is_first_quarter_2024 = quarter == 1 and reference_date.year == 2024

    # the reference date is in the last 10 days of its quarter
    # this means the wanted quarter is the reference date's quarter
    if (last_day_of_quarter - reference_date).days <= 10:
        return quarter, last_day_of_quarter.year

    # the reference date is in the first 20 days of its quarter
    # this means the wanted quarter is the quarter before the reference date's
    if (reference_date - first_day_of_quarter).days <= 20 or is_first_quarter_2024:
        previous_quarter = quarter - 1 if quarter > 1 else 4
        previous_quarter_year = first_day_of_quarter.year if quarter > 1 else first_day_of_quarter.year - 1
        return previous_quarter, previous_quarter_year

    return None, None
