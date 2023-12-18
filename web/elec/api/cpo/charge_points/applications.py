from django.views.decorators.http import require_GET
from core.common import SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.serializers.elec_charge_point_application import ElecChargePointApplicationSerializer
from elec.services.get_annotated_applications import get_annotated_applications


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_applications(request, entity):
    applications = get_annotated_applications(entity)
    serialized = ElecChargePointApplicationSerializer(applications, many=True).data
    return SuccessResponse(serialized)