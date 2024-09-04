from django.views.decorators.http import require_POST

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.models import ElecChargePointApplication
from elec.serializers.elec_charge_point import ElecChargePointUpdateSerializer


class ChargePointUpdateError:
    CP_NOT_FOUND_ON_CPO = "CP_NOT_FOUND_ON_CPO"
    CP_CANNOT_BE_UPDATED = "CP_CANNOT_BE_UPDATED"


@require_POST
@check_user_rights(entity_type=[Entity.CPO])
def update_charge_point(request, entity, entity_id):
    serializer = ElecChargePointUpdateSerializer(data=request.POST, partial=True)
    if not serializer.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, serializer.errors)

    cp = serializer.validated_data["id"]

    if cp.cpo != entity:
        return ErrorResponse(400, ChargePointUpdateError.CP_NOT_FOUND_ON_CPO)

    validated_data = serializer.validated_data

    if "charge_point_id" in validated_data and cp.application.status != ElecChargePointApplication.PENDING:
        return ErrorResponse(400, ChargePointUpdateError.CP_CANNOT_BE_UPDATED)

    if "charge_point_id" in validated_data:
        cp.charge_point_id = validated_data["charge_point_id"]

    if "measure_reference_point_id" in validated_data:
        cp.measure_reference_point_id = validated_data["measure_reference_point_id"]

    cp.save()

    return SuccessResponse()
