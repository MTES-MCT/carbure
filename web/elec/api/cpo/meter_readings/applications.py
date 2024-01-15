from django.views.decorators.http import require_GET
from core.common import SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.serializers.elec_meter_reading_application_serializer import ElecMeterReadingApplicationSerializer


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_applications(request, entity):
    applications = MeterReadingRepository.get_annotated_applications(entity)
    serialized = ElecMeterReadingApplicationSerializer(applications, many=True).data
    return SuccessResponse(serialized)
