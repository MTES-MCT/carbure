# /api/saf/airline/accept-ticket

import traceback
from django.db import transaction
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicket, create_source_from_ticket
from core.models import UserRights, CarbureNotification


class SafTicketAcceptError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    TICKET_ACCEPTANCE_FAILED = "TICKET_ACCEPTANCE_FAILED"
    TICKET_NOT_FOUND = "TICKET_NOT_FOUND"


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def credit_ticket_source(request, *args, **kwargs):
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
        with transaction.atomic():
            ticket.status = SafTicket.ACCEPTED
            ticket.save()

            create_source_from_ticket(ticket, entity_id)

            CarbureNotification.objects.create(
                type=CarbureNotification.SAF_TICKET_ACCEPTED,
                dest_id=ticket.supplier_id,
                send_by_email=False,
                meta={"client": ticket.client.name, "ticket_id": ticket.id, "year": ticket.year},
            )

        return SuccessResponse()
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketAcceptError.TICKET_ACCEPTANCE_FAILED)
