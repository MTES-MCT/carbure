from datetime import date
from django.views.decorators.http import require_GET
from core.common import SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity

from elec.repositories.charge_point_repository import ChargePointRepository
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.serializers.elec_meter_reading_application import ElecMeterReadingApplicationSerializer

import elec.services.meter_readings_application_quarter as quarters


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_applications(request, entity):
    current_date = date.today()
    year, quarter = quarters.get_application_quarter(current_date)
    deadline, urgency_status = quarters.get_application_deadline(current_date, year, quarter)

    current_application = MeterReadingRepository.get_cpo_application_for_quarter(entity, year, quarter)
    applications = MeterReadingRepository.get_annotated_applications_by_cpo(entity)

    prefetched_charge_points_for_meter_readings_count = ChargePointRepository.get_charge_points_for_meter_readings(
        entity
    ).count()

    serialized_applications = ElecMeterReadingApplicationSerializer(applications, many=True).data
    serialized_current_application = ElecMeterReadingApplicationSerializer(current_application).data if current_application else None  # fmt:skip

    return SuccessResponse(
        {
            "applications": serialized_applications,
            "current_application": serialized_current_application,
            "current_application_period": {
                "year": year,
                "quarter": quarter,
                "deadline": str(deadline),
                "urgency_status": urgency_status,
                "charge_point_count": prefetched_charge_points_for_meter_readings_count,
            },
        }
    )
