# /api/v5/saf/operator/cancel-ticket

import traceback
from django.db import transaction
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicket
from core.models import UserRights


class SafTicketCancelError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    TICKET_CANCELLATION_FAILED = "TICKET_CANCELLATION_FAILED"
    TICKET_NOT_FOUND = "TICKET_NOT_FOUND"


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def cancel_ticket(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
        ticket_id = int(request.POST.get("ticket_id"))
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketCancelError.MALFORMED_PARAMS)

    try:
        ticket = SafTicket.objects.get(id=ticket_id, supplier_id=entity_id)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketCancelError.TICKET_NOT_FOUND)

    try:
        with transaction.atomic():
            ticket.parent_ticket_source.assigned_volume -= ticket.volume
            ticket.parent_ticket_source.save()
            ticket.delete()

        return SuccessResponse()
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketCancelError.TICKET_CANCELLATION_FAILED)
