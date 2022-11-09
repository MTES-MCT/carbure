# /api/v5/saf/airline/reject-ticket

import traceback
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicket
from core.models import UserRights


class SafTicketRejectError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    TICKET_REJECTION_FAILED = "TICKET_REJECTION_FAILED"
    TICKET_NOT_FOUND = "TICKET_NOT_FOUND"


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def reject_ticket(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
        ticket_id = int(request.POST.get("ticket_id"))
        comment = request.POST.get("comment")
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketRejectError.MALFORMED_PARAMS)

    try:
        ticket = SafTicket.objects.get(id=ticket_id, client_id=entity_id)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketRejectError.TICKET_NOT_FOUND)

    try:
        ticket.status = SafTicket.REJECTED
        ticket.client_comment = comment
        ticket.save()

        return SuccessResponse()
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketRejectError.TICKET_REJECTION_FAILED)
