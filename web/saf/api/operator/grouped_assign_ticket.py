# /api/saf/operator/assign-ticket

import traceback

from django.db import transaction
from django.db.models.aggregates import Max, Sum

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import CarbureNotification, UserRights
from saf.models import SafTicketSource, create_ticket_from_source


class SafTicketGroupedAssignError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    VOLUME_TOO_BIG = "VOLUME_TOO_BIG"
    TICKET_CREATION_FAILED = "TICKET_CREATION_FAILED"
    TICKET_SOURCE_NOT_FOUND = "TICKET_SOURCE_NOT_FOUND"
    ASSIGNMENT_BEFORE_DELIVERY = "ASSIGNMENT_BEFORE_DELIVERY"


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def grouped_assign_ticket(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
        ticket_sources_ids = [int(id) for id in request.POST.getlist("ticket_sources_ids")]
        client_id = int(request.POST.get("client_id"))
        volume = float(request.POST.get("volume"))
        agreement_reference = request.POST.get("agreement_reference")
        agreement_date = request.POST.get("agreement_date")
        free_field = request.POST.get("free_field")
        assignment_period = int(request.POST.get("assignment_period"))
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketGroupedAssignError.MALFORMED_PARAMS)

    try:
        ticket_sources = SafTicketSource.objects.filter(id__in=ticket_sources_ids, added_by_id=entity_id).order_by("created_at")  # fmt:skip
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketGroupedAssignError.TICKET_SOURCE_NOT_FOUND)

    try:
        total_volume_in_selection = ticket_sources.aggregate(Sum("total_volume"))["total_volume__sum"]
        assigned_volume_in_selection = ticket_sources.aggregate(Sum("assigned_volume"))["assigned_volume__sum"]
        if volume > (total_volume_in_selection - assigned_volume_in_selection):
            return ErrorResponse(400, SafTicketGroupedAssignError.VOLUME_TOO_BIG)

        # use the most recent period of all the selected ticket sources to decide if the asked period is ok
        most_recent_period = ticket_sources.aggregate(Max("delivery_period"))["delivery_period__max"]
        if assignment_period < most_recent_period:
            return ErrorResponse(400, SafTicketGroupedAssignError.ASSIGNMENT_BEFORE_DELIVERY)

        with transaction.atomic():
            assigned_tickets_count = 0
            remaining_volume_to_assign = volume

            for ticket_source in ticket_sources:
                # create a ticket with a volume taking into account:
                # - what's left in the ticket source
                available_volume_in_source = ticket_source.total_volume - ticket_source.assigned_volume
                # - and what's left in the amount asked by the user
                ticket_volume = min(remaining_volume_to_assign, available_volume_in_source)

                # do not
                if ticket_volume <= 0:
                    break

                ticket = create_ticket_from_source(
                    ticket_source,
                    client_id=client_id,
                    volume=ticket_volume,
                    agreement_date=agreement_date,
                    agreement_reference=agreement_reference,
                    assignment_period=assignment_period,
                    free_field=free_field,
                )

                CarbureNotification.objects.create(
                    type=CarbureNotification.SAF_TICKET_RECEIVED,
                    dest_id=client_id,
                    send_by_email=False,
                    meta={"supplier": ticket.supplier.name, "ticket_id": ticket.id, "year": ticket.year},
                )

                assigned_tickets_count += 1
                ticket_source.assigned_volume += ticket.volume
                remaining_volume_to_assign -= ticket.volume
                ticket_source.save()

        return SuccessResponse({"assigned_tickets_count": assigned_tickets_count})
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketGroupedAssignError.TICKET_CREATION_FAILED)
