# /api/v5/saf/airline/accept-ticket

import traceback
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicket
from core.models import UserRights


class SafTicketAcceptError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    TICKET_ACCEPTANCE_FAILED = "TICKET_REJECTION_FAILED"
    TICKET_NOT_FOUND = "TICKET_NOT_FOUND"


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def accept_ticket(request, *args, **kwargs):
    try:
        entity_id = int(request.POST.get("entity_id"))
        ticket_id = int(request.POST.get("ticket_id"))
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketAcceptError.MALFORMED_PARAMS)

    try:
        ticket = SafTicket.objects.get(id=ticket_id, client_id=entity_id)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketAcceptError.TICKET_NOT_FOUND)

    try:
        ticket.status = SafTicket.ACCEPTED
        ticket.save()

        return SuccessResponse()
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketAcceptError.TICKET_ACCEPTANCE_FAILED)
