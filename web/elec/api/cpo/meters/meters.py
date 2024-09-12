from django.views.decorators.http import require_GET

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.models import ElecMeter
from elec.serializers.elec_charge_point import ElecChargePointIdSerializer
from elec.serializers.elec_meter import ElecMeterSerializer


class MetersError:
    CP_NOT_FOUND_ON_CPO = "CP_NOT_FOUND_ON_CPO"


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_meters(request, entity):
    serializer = ElecChargePointIdSerializer(data=request.GET)

    if not serializer.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, serializer.errors)

    cp = serializer.validated_data["charge_point_id"]

    if cp.cpo != entity:
        return ErrorResponse(400, MetersError.CP_NOT_FOUND_ON_CPO)

    meters = ElecMeter.objects.filter(charge_point=cp)

    serialized = ElecMeterSerializer(meters, many=True).data
    return SuccessResponse(serialized)
