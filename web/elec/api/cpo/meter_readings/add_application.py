from datetime import date
from django.http import HttpRequest
from django.db import transaction
from django.views.decorators.http import require_POST
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.api.cpo.meter_readings.application_template import first_day_of_current_quarter
from elec.api.cpo.meter_readings.check_application import get_last_quarter
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.services.import_meter_reading_excel import import_meter_reading_excel


class AddMeterReadingApplicationError:
    TOO_LATE = "TOO_LATE"
    MISSING_FILE = "MISSING_FILE"
    VALIDATION_FAILED = "VALIDATION_FAILED"


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW], entity_type=[Entity.CPO])
def add_application(request: HttpRequest, entity: Entity):
    excel_file = request.FILES.get("file")

    if not excel_file:
        return ErrorResponse(400, AddMeterReadingApplicationError.MISSING_FILE)

    existing_charge_points = ElecChargePoint.objects.select_related("application").filter(
        cpo=entity, application__status=ElecChargePointApplication.ACCEPTED
    )

    meter_reading_data, errors = import_meter_reading_excel(excel_file, existing_charge_points)

    if len(errors) > 0:
        return ErrorResponse(400, AddMeterReadingApplicationError.VALIDATION_FAILED)

    today = date.today()
    first_day = first_day_of_current_quarter()
    quarter, year = get_last_quarter()

    if (today - first_day).days > 20:
        return ErrorResponse(400, AddMeterReadingApplicationError.TOO_LATE)

    with transaction.atomic():
        replaced_applications = ElecMeterReadingApplication.objects.filter(
            cpo=entity, status__in=[ElecMeterReadingApplication.PENDING, ElecMeterReadingApplication.REJECTED]
        )

        # delete older pending applications
        replaced_applications.delete()

        application = ElecMeterReadingApplication(cpo=entity, quarter=quarter, year=year)
        meter_readings = [ElecMeterReading(**data, application=application, cpo=entity) for data in meter_reading_data]

        application.save()
        ElecMeterReading.objects.bulk_create(meter_readings)

    return SuccessResponse()
