from django.views.decorators.http import require_POST

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.serializers.elec_charge_point import ElecChargePointUpdateSerializer
from elec.services.transport_data_gouv import TransportDataGouv


class ChargePointUpdateError:
    CP_NOT_FOUND_ON_CPO = "CP_NOT_FOUND_ON_CPO"
    CP_CANNOT_BE_UPDATED = "CP_CANNOT_BE_UPDATED"
    AUDIT_IN_PROGRESS = "AUDIT_IN_PROGRESS"
    CP_ID_NOT_IN_TGD = "CP_ID_NOT_IN_TGD"
    CP_ID_ALREADY_EXISTS = "CP_ID_ALREADY_EXISTS"
    INITIAL_INDEX_CANNOT_BE_UPDATED = "INITIAL_INDEX_CANNOT_BE_UPDATED"
    INITIAL_INDEX_CANNOT_BE_UPDATED_FOR_DC = "INITIAL_INDEX_CANNOT_BE_UPDATED_FOR_DC"


@require_POST
@check_user_rights(entity_type=[Entity.CPO])
def update_charge_point(request, entity, entity_id):
    serializer = ElecChargePointUpdateSerializer(data=request.POST, partial=False)
    if not serializer.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, serializer.errors)

    cp = serializer.validated_data["id"]

    if cp.cpo != entity:
        return ErrorResponse(400, ChargePointUpdateError.CP_NOT_FOUND_ON_CPO)

    validated_data = serializer.validated_data

    if "measure_reference_point_id" in validated_data:
        return ErrorResponse(400, ChargePointUpdateError.CP_CANNOT_BE_UPDATED)

    if not cp.is_updatable():
        return ErrorResponse(400, ChargePointUpdateError.AUDIT_IN_PROGRESS)

    if not TransportDataGouv.is_check_point_in_tdg(validated_data["charge_point_id"]):
        return ErrorResponse(400, ChargePointUpdateError.CP_ID_NOT_IN_TGD)

    if cp.charge_point_id != validated_data["charge_point_id"]:
        existing_charge_points = ChargePointRepository.get_replaced_charge_points(
            entity, [validated_data["charge_point_id"]]
        )
        if existing_charge_points.exists():
            return ErrorResponse(400, ChargePointUpdateError.CP_ID_ALREADY_EXISTS)

    cp.charge_point_id = validated_data["charge_point_id"]
    cp.save()

    # Update initial index of current meter
    # Only if there are no meter readings yet
    if "initial_index" in validated_data:
        if cp.current_meter:  # AC power case
            if not cp.current_meter.elec_meter_readings.exists():
                cp.current_meter.initial_index = validated_data["initial_index"]
                cp.current_meter.save()
            else:
                return ErrorResponse(400, ChargePointUpdateError.INITIAL_INDEX_CANNOT_BE_UPDATED)
        else:
            return ErrorResponse(400, ChargePointUpdateError.INITIAL_INDEX_CANNOT_BE_UPDATED_FOR_DC)

    return SuccessResponse()
