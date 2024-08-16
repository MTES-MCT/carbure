from django import forms
from django.views.decorators.http import require_POST
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from elec.models import ElecChargePointApplication
from core.models import Entity
from elec.serializers.elec_charge_point import ElecChargePointUpdateSerializer
from core.carburetypes import CarbureError


class ChargePointUpdateError:
    CP_NOT_FOUND_ON_CPO = "CP_NOT_FOUND_ON_CPO"
    CP_CANNOT_BE_UPDATED = "CP_CANNOT_BE_UPDATED"


@require_POST
@check_user_rights(entity_type=[Entity.CPO])
def update_charge_point(request, entity, entity_id):
    serializer = ElecChargePointUpdateSerializer(data=request.POST)

    if not serializer.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, serializer.errors)

    cp = serializer.validated_data["id"]

    if cp.cpo != entity:
        return ErrorResponse(400, ChargePointUpdateError.CP_NOT_FOUND_ON_CPO)

    if cp.application.status != ElecChargePointApplication.PENDING:
        return ErrorResponse(400, ChargePointUpdateError.CP_CANNOT_BE_UPDATED)

    cp.charge_point_id = serializer.validated_data["charge_point_id"]
    cp.save()

    return SuccessResponse()
