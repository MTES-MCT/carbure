# /api/v5/saf/operator/tickets/details

import traceback

from django.db.models import Q
from core.common import SuccessResponse, ErrorResponse
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
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketError.MALFORMED_PARAMS)

    try:
        ticket_filter = Q(id=ticket_id) & (Q(supplier_id=entity_id) | Q(client_id=entity_id))
        ticket = SafTicket.objects.select_related("parent_ticket_source").get(ticket_filter)
        serialized = SafTicketDetailsSerializer(ticket)
        return SuccessResponse(serialized.data)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketError.TICKET_DETAILS_FAILED)
