from datetime import date, timedelta
from django.http import HttpRequest
from django.views.decorators.http import require_POST
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.services.import_meter_reading_excel import import_meter_reading_excel


class CheckMeterReadingApplicationError:
    MISSING_FILE = "MISSING_FILE"
    VALIDATION_FAILED = "VALIDATION_FAILED"


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW], entity_type=[Entity.CPO])
def check_application(request: HttpRequest, entity):
    excel_file = request.FILES.get("file")

    if not excel_file:
        return ErrorResponse(400, CheckMeterReadingApplicationError.MISSING_FILE)

    existing_charge_points = ElecChargePoint.objects.select_related("application").filter(
        cpo=entity, application__status=ElecChargePointApplication.ACCEPTED
    )

    meter_reading_data, errors = import_meter_reading_excel(excel_file, existing_charge_points)

    replaceable_applications = ElecMeterReadingApplication.objects.filter(
        cpo=entity, status__in=[ElecMeterReadingApplication.PENDING, ElecMeterReadingApplication.REJECTED]
    )

    quarter, year = get_last_quarter()

    data = {}
    data["file_name"] = excel_file.name
    data["meter_reading_count"] = len(meter_reading_data)
    data["quarter"] = quarter
    data["year"] = year
    data["errors"] = []
    data["error_count"] = 0
    data["pending_application_already_exists"] = replaceable_applications.count() > 0

    if len(errors) > 0:
        data["errors"] = errors
        data["error_count"] = len(data["errors"])
        return ErrorResponse(400, CheckMeterReadingApplicationError.VALIDATION_FAILED, data)

    return SuccessResponse(data)


def get_last_quarter():
    first_day_of_current = first_day_of_current_quarter()
    last_day_of_previous = first_day_of_current - timedelta(days=1)
    quarter = (last_day_of_previous.month - 1) // 3 + 1
    year = last_day_of_previous.year if quarter != 1 else last_day_of_previous.year - 1
    return quarter, year


def first_day_of_current_quarter():
    now = date.today()
    quarter = (now.month - 1) // 3 + 1
    month = (quarter - 1) * 3 + 1
    return date(now.year, month, 1)
