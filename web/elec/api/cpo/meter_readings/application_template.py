import traceback
from datetime import date
from django.views.decorators.http import require_GET
from core.common import ErrorResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.models import UserRights
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.api.cpo.meter_readings.check_application import get_application_quarter
from elec.services.create_meter_reading_excel import create_meter_readings_data, create_meter_readings_excel


class ApplicationTemplateError:
    TOO_LATE = "TOO_LATE"
    NO_CHARGE_POINT_AVAILABLE = "NO_CHARGE_POINT_AVAILABLE"


@require_GET
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def get_application_template(request, entity):
    quarter, year = get_application_quarter(date.today())
    if not quarter or not year:
        return ErrorResponse(400, ApplicationTemplateError.TOO_LATE)

    charge_points = ChargePointRepository.get_registered_charge_points(entity)

    if charge_points.count() == 0:
        return ErrorResponse(400, ApplicationTemplateError.NO_CHARGE_POINT_AVAILABLE)

    previous_application = MeterReadingRepository.get_previous_application(entity, quarter, year)
    meter_reading_data = create_meter_readings_data(charge_points, previous_application)

    file_name = f"meter_reading_template_Q{quarter}_{year}"
    excel_file = create_meter_readings_excel(file_name, quarter, year, meter_reading_data)
    return ExcelResponse(excel_file)
