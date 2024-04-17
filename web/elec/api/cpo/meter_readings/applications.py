from datetime import date
from django.views.decorators.http import require_GET
from core.common import SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.helpers.meter_readings_application_quarter import (
    get_application_deadline,
    get_application_quarter,
)
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.serializers.elec_meter_reading_application import ElecMeterReadingApplicationSerializer


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_applications(request, entity):
    current_date = date.today()
    year, quarter = get_application_quarter(current_date)
    print(">>>quarter: ", quarter)
    deadline, urgency_status = get_application_deadline(current_date, year, quarter)

    current_application = MeterReadingRepository.get_cpo_application_for_quarter(entity, year, quarter)
    applications = MeterReadingRepository.get_annotated_applications_by_cpo(entity)

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
            },
        }
    )
