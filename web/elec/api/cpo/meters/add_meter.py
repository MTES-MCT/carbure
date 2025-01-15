from django.views.decorators.http import require_POST

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.serializers.elec_meter import ElecMeterSerializer


class MetersError:
    CP_NOT_FOUND_ON_CPO = "CP_NOT_FOUND_ON_CPO"
    AUDIT_IN_PROGRESS = "AUDIT_IN_PROGRESS"
    NEW_INITIAL_INDEX_DATE_KO = "NEW_INITIAL_INDEX_DATE_KO"


@require_POST
@check_user_rights(entity_type=[Entity.CPO])
def add_elec_meter(request, entity, entity_id):
    serializer = ElecMeterSerializer(data=request.POST)

    if not serializer.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, data=serializer.errors)

    if serializer.validated_data["charge_point"].cpo != entity:
        return ErrorResponse(400, MetersError.CP_NOT_FOUND_ON_CPO)

    if not serializer.validated_data["charge_point"].is_updatable():
        return ErrorResponse(400, MetersError.AUDIT_IN_PROGRESS)

    if (
        serializer.validated_data["charge_point"].current_meter
        and serializer.validated_data["charge_point"].current_meter.elec_meter_readings.exists()
    ):
        last_meter_reading_date = (
            serializer.validated_data["charge_point"].current_meter.elec_meter_readings.last().reading_date
        )
        new_initial_index_date = serializer.validated_data["initial_index_date"]

        if new_initial_index_date <= last_meter_reading_date:
            return ErrorResponse(400, MetersError.NEW_INITIAL_INDEX_DATE_KO)

    meter = serializer.save()

    # Update the current meter of the charge point
    cp = meter.charge_point
    cp.current_meter = meter
    cp.save()

    return SuccessResponse()
