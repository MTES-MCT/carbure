# /api/saf/airline/tickets/details

import traceback

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from saf.models import SafTicket
from saf.serializers import SafTicketDetailsSerializer


class SafTicketError:
    TICKET_DETAILS_FAILED = "TICKET_DETAILS_FAILED"
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


@check_user_rights()
def get_ticket_details(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
        ticket_id = int(request.GET.get("ticket_id"))
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketError.MALFORMED_PARAMS)

    try:
        ticket = SafTicket.objects.select_related("parent_ticket_source").get(id=ticket_id, client_id=entity_id)
        serialized = SafTicketDetailsSerializer(ticket)
        return SuccessResponse(serialized.data)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketError.TICKET_DETAILS_FAILED)
