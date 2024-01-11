import traceback
from datetime import date
from typing import Iterable
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from core.common import ErrorResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.models import UserRights
from elec.api.cpo.meter_readings.check_application import get_application_quarter
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.services.create_meter_reading_excel import MeterReadingData, create_meter_reading_excel


class ApplicationTemplateError:
    TOO_LATE = "TOO_LATE"
    NO_CHARGE_POINT_AVAILABLE = "NO_CHARGE_POINT_AVAILABLE"
    TEMPLATE_CREATION_FAILED = "TEMPLATE_CREATION_FAILED"


@require_GET
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def get_application_template(request, entity):
    quarter, year = get_application_quarter(date.today())
    if not quarter or not year:
        return ErrorResponse(400, ApplicationTemplateError.TOO_LATE)

    try:
        charge_points = ChargePointRepository.get_registered_charge_points(entity)

        if charge_points.count() == 0:
            return ErrorResponse(400, ApplicationTemplateError.NO_CHARGE_POINT_AVAILABLE)

        last_application = MeterReadingRepository.get_last_application(entity, quarter, year)
        meter_reading_data = create_meter_reading_data(last_application, charge_points)

        file_name = "meter_reading_template"
        excel_file = create_meter_reading_excel(file_name, quarter, year, meter_reading_data)
        return ExcelResponse(excel_file)
    except:
        traceback.print_exc()
        return ErrorResponse(400, ApplicationTemplateError.TEMPLATE_CREATION_FAILED)


def create_meter_reading_data(last_application: ElecMeterReadingApplication, charge_points: Iterable[ElecChargePoint]):
    meter_reading_data: list[MeterReadingData] = []
    last_readings_by_charge_point = {}

    if last_application:
        for reading in last_application.elec_meter_readings.all():
            last_readings_by_charge_point[reading.charge_point.charge_point_id] = reading.extracted_energy
    else:
        for charge_point in charge_points:
            last_readings_by_charge_point[charge_point.charge_point_id] = charge_point.measure_energy

    for charge_point in charge_points:
        meter_reading_data.append(
            {
                "charge_point_id": charge_point.charge_point_id,
                "previous_reading": last_readings_by_charge_point.get(charge_point.charge_point_id, 0),
            }
        )

    return meter_reading_data
