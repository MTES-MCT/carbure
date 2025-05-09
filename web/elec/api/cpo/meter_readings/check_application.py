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
from elec.services.meter_readings_application_quarter import (
    first_day_of_quarter,
    get_application_quarter,
    last_day_of_quarter,
)


class CheckMeterReadingApplicationForm(forms.Form):
    quarter = forms.IntegerField(required=False)
    year = forms.IntegerField(required=False)


class CheckMeterReadingApplicationError:
    TOO_LATE = "TOO_LATE"
    MISSING_FILE = "MISSING_FILE"
    NO_READING_FOUND = "NO_READING_FOUND"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    METER_READINGS_FOR_QUARTER_ALREADY_EXISTS = "METER_READINGS_FOR_QUARTER_ALREADY_EXISTS"


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

    if MeterReadingRepository.get_cpo_application_for_quarter(cpo=entity, year=year, quarter=quarter) is not None:
        return ErrorResponse(400, CheckMeterReadingApplicationError.METER_READINGS_FOR_QUARTER_ALREADY_EXISTS)

    charge_points = ChargePointRepository.get_registered_charge_points(entity)
    renewable_share = MeterReadingRepository.get_renewable_share(year)

    # get the first and last day of this quarter so we can verify that the readings are for the current quarter
    beginning_of_quarter = first_day_of_quarter(year, quarter)
    end_of_quarter = last_day_of_quarter(year, quarter) + timedelta(days=15)

    meter_reading_data, errors = import_meter_reading_excel(
        excel_file,
        charge_points,
        renewable_share,
        beginning_of_quarter,
        end_of_quarter,
    )

    data = {}
    data["file_name"] = excel_file.name
    data["meter_reading_count"] = len(meter_reading_data)
    data["quarter"] = quarter
    data["year"] = year
    data["errors"] = []
    data["error_count"] = 0

    if len(errors) > 0:
        for error in errors:
            error["meta"].pop("meter", None)
        data["errors"] = [error for error in errors if error["meta"]]

        data["error_count"] = len(data["errors"])
        return ErrorResponse(400, CheckMeterReadingApplicationError.VALIDATION_FAILED, data)

    if len(meter_reading_data) == 0:
        return ErrorResponse(400, CheckMeterReadingApplicationError.NO_READING_FOUND, data)

    return SuccessResponse(data)
