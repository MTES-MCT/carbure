# /api/v5/saf/tickets

from math import floor
import traceback
from django.core.paginator import Paginator
from django.db.models.expressions import F

from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicket
from saf.serializers import SafTicketSerializer


class SafTicketError:
    TICKET_LISTING_FAILED = "TICKET_LISTING_FAILED"
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


@check_user_rights()
def get_tickets(request, *args, **kwargs):
    try:
        query = parse_ticket_query(request.GET)
        from_idx = int(request.GET.get("from_idx", 0))
        limit = int(request.GET.get("limit", 25))
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketError.MALFORMED_PARAMS)

    try:
        tickets = find_tickets(**query)

        paginator = Paginator(tickets, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)

        ids = tickets.values_list("id", flat=True)
        serialized = SafTicketSerializer(page.object_list, many=True)

        return SuccessResponse(
            {
                "saf_tickets": serialized.data,
                "ids": list(ids),
                "from": from_idx,
                "returned": len(serialized.data),
                "total": len(ids),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketError.TICKET_LISTING_FAILED)


def parse_ticket_query(query):
    entity_id = int(query["entity_id"])
    status = query["status"]
    year = int(query["year"])
    period = [int(p) for p in query.getlist("period")] if "period" in query else None
    client = query.getlist("client") if "client" in query else None
    feedstock = query.getlist("feedstock") if "feedstock" in query else None

    return {
        "entity_id": entity_id,
        "year": year,
        "period": period,
        "status": status,
        "feedstock": feedstock,
        "client": client,
    }


def find_tickets(**filters):
    tickets = SafTicket.objects.select_related("parent_ticket_source")

    if filters["entity_id"] != None:
        tickets = tickets.filter(supplier_id=filters["entity_id"])

    if filters["year"] != None:
        tickets = tickets.filter(year=filters["year"])

    if filters["period"] != None:
        tickets = tickets.filter(period__in=filters["period"])

    if filters["feedstock"] != None:
        tickets = tickets.filter(feedstock__code__in=filters["feedstock"])

    if filters["client"] != None:
        tickets = tickets.filter(client__name__in=filters["client"])

    if filters["status"] == "pending":
        tickets = tickets.filter(status=SafTicket.PENDING)
    elif filters["status"] == "accepted":
        tickets = tickets.filter(status=SafTicket.ACCEPTED)
    elif filters["status"] == "rejected":
        tickets = tickets.filter(status=SafTicket.REJECTED)
    else:
        raise Exception("Status '%s' does not exist for tickets" % filters["status"])

    return tickets
