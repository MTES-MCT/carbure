# /api/v5/saf/operator/assign-ticket

import traceback
from django.db import transaction
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicketSource, create_ticket_from_source
from core.models import UserRights, CarbureNotification


class SafTicketAssignError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    VOLUME_TOO_BIG = "VOLUME_TOO_BIG"
    TICKET_CREATION_FAILED = "TICKET_CREATION_FAILED"
    TICKET_SOURCE_NOT_FOUND = "TICKET_SOURCE_NOT_FOUND"
    ASSIGNMENT_BEFORE_DELIVERY = "ASSIGNMENT_BEFORE_DELIVERY"


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def assign_ticket(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
        ticket_source_id = int(request.POST.get("ticket_source_id"))
        client_id = int(request.POST.get("client_id"))
        volume = float(request.POST.get("volume"))
        agreement_reference = request.POST.get("agreement_reference")
        agreement_date = request.POST.get("agreement_date")
        free_field = request.POST.get("free_field")
        assignment_period = int(request.POST.get("assignment_period"))
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketAssignError.MALFORMED_PARAMS)

    try:
        ticket_source = SafTicketSource.objects.get(id=ticket_source_id, added_by_id=entity_id)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketAssignError.TICKET_SOURCE_NOT_FOUND)

    if volume > (ticket_source.total_volume - ticket_source.assigned_volume):
        return ErrorResponse(400, SafTicketAssignError.VOLUME_TOO_BIG)

    if assignment_period < ticket_source.delivery_period:
        return ErrorResponse(400, SafTicketAssignError.ASSIGNMENT_BEFORE_DELIVERY)

    try:
        with transaction.atomic():
            ticket = create_ticket_from_source(
                ticket_source,
                client_id=client_id,
                volume=volume,
                agreement_date=agreement_date,
                agreement_reference=agreement_reference,
                assignment_period=assignment_period,
                free_field=free_field
            )

            CarbureNotification.objects.create(
                type=CarbureNotification.SAF_TICKET_RECEIVED,
                dest_id=client_id,
                send_by_email=False,
                meta={"supplier": ticket.supplier.name, "ticket_id": ticket.id, "year": ticket.year},
            )

            ticket_source.assigned_volume += ticket.volume
            ticket_source.save()

        return SuccessResponse()
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketAssignError.TICKET_CREATION_FAILED)
