# /api/v5/saf/airline/tickets

from math import floor
import traceback
from django.core.paginator import Paginator
from django.db.models import Q

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
    print("******")
    print(status)
    print("******")
    year = int(query["year"])
    search = query.get("search", None)
    periods = [int(p) for p in query.getlist("periods")] if "periods" in query else None
    suppliers = query.getlist("suppliers") if "suppliers" in query else None
    feedstocks = query.getlist("feedstocks") if "feedstocks" in query else None

    return {
        "entity_id": entity_id,
        "status": status,
        "year": year,
        "periods": periods,
        "feedstocks": feedstocks,
        "suppliers": suppliers,
        "search": search,
    }


def find_tickets(**filters):
    tickets = SafTicket.objects.select_related(
        "parent_ticket_source",
        "feedstock",
        "biofuel",
        "country_of_origin",
        "carbure_production_site",
        "supplier",
    )

    if filters["entity_id"] != None:
        tickets = tickets.filter(client_id=filters["entity_id"])

    if filters["year"] != None:
        tickets = tickets.filter(year=filters["year"])

    if filters["periods"] != None:
        tickets = tickets.filter(period__in=filters["periods"])

    if filters["feedstocks"] != None:
        tickets = tickets.filter(feedstock__code__in=filters["feedstocks"])

    if filters["suppliers"] != None:
        tickets = tickets.filter(supplier__name__in=filters["suppliers"])

    if filters["status"] == SafTicket.PENDING:
        tickets = tickets.filter(status=SafTicket.PENDING)
    elif filters["status"] == SafTicket.ACCEPTED:
        tickets = tickets.filter(status=SafTicket.ACCEPTED)
    else:
        raise Exception("Status '%s' does not exist for tickets" % filters["status"])

    if filters["search"] != None:
        tickets = tickets.filter(
            Q(carbure_id__icontains=filters["search"])
            | Q(supplier__name__icontains=filters["search"])
            | Q(feedstock__name__icontains=filters["search"])
            | Q(biofuel__name__icontains=filters["search"])
            | Q(country_of_origin__name__icontains=filters["search"])
            | Q(agreement_reference__icontains=filters["search"])
            | Q(carbure_production_site__name__icontains=filters["search"])
            | Q(unknown_production_site__icontains=filters["search"])
        )

    return tickets
