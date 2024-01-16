from django.db import transaction
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.helpers import filter_lots, get_entity_lots_by_status
from core.models import CarbureLot, CarbureLotEvent, Entity, UserRights


class AcceptConsumptionError:
    VALIDATION_FAILED = "VALIDATION_FAILED"
    NOT_CLIENT = "NOT_CLIENT"
    INVALID_STATUS = "INVALID_STATUS"


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN], entity_type=[Entity.POWER_STATION])
def accept_consumption(request, entity, entity_id):
    status = request.POST.get("status", False)

    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity)

    updated_lots = []
    accepted_events = []
    errors = []

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
            errors.append({"error": AcceptConsumptionError.NOT_CLIENT, "meta": {"lot_id": lot.id}})
            continue

        if lot.lot_status != CarbureLot.PENDING:
            errors.append({"error": AcceptConsumptionError.INVALID_STATUS, "meta": {"lot_id": lot.id, "status": lot.lot_status}})  # fmt: skip
            continue

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.CONSUMPTION
        updated_lots.append(lot)

        event = CarbureLotEvent(event_type=CarbureLotEvent.ACCEPTED, lot=lot, user=request.user)
        accepted_events.append(event)

    if len(errors) > 0:
        return ErrorResponse(400, AcceptConsumptionError.VALIDATION_FAILED, errors)

    with transaction.atomic():
        CarbureLot.objects.bulk_update(updated_lots, ["lot_status", "delivery_type"])
        CarbureLotEvent.objects.bulk_create(accepted_events)

    return SuccessResponse()
