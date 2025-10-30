from django.db import transaction
from django.views.decorators.http import require_POST

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.models.elec_charge_point import ElecChargePoint


class MetersError:
    METER_NOT_FOUND = "METER_NOT_FOUND"
    AUDIT_IN_PROGRESS = "AUDIT_IN_PROGRESS"
    READINGS_ALREADY_REGISTERED = "READINGS_ALREADY_REGISTERED"


@require_POST
@check_user_rights(entity_type=[Entity.CPO])
def delete_elec_meter(request, entity, entity_id):
    charge_point_id = request.POST.get("charge_point_id")

    if not charge_point_id:
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS)

    charge_point = ElecChargePoint.objects.filter(pk=charge_point_id, cpo=entity).select_related("current_meter").first()

    if not charge_point or not charge_point.current_meter:
        return ErrorResponse(400, MetersError.METER_NOT_FOUND)

    if not charge_point.is_updatable():
        return ErrorResponse(400, MetersError.AUDIT_IN_PROGRESS)

    if charge_point.current_meter.elec_meter_readings.exists():
        return ErrorResponse(400, MetersError.READINGS_ALREADY_REGISTERED)

    with transaction.atomic():
        charge_point.current_meter.delete()
        charge_point.current_meter = None
        charge_point.save()

    return SuccessResponse()
