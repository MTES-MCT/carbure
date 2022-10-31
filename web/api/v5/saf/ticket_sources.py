# /api/v5/saf/ticket-sources

from math import floor
import traceback
from django.core.paginator import Paginator
from django.db.models.expressions import F

from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicketSource
from saf.serializers import SafTicketSourceSerializer


class SafTicketSourceError:
    TICKET_SOURCE_LISTING_FAILED = "TICKET_SOURCE_LISTING_FAILED"
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


@check_user_rights()
def get_ticket_sources(request, *args, **kwargs):
    try:
        query = parse_ticket_source_query(request.GET)
        from_idx = int(request.GET.get("from_idx", 0))
        limit = int(request.GET.get("limit", 25))
    except:
        return ErrorResponse(400, SafTicketSourceError.MALFORMED_PARAMS)

    try:
        ticket_sources = find_ticket_sources(**query)

        paginator = Paginator(ticket_sources, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)

        ids = ticket_sources.values_list("id", flat=True)
        serialized = SafTicketSourceSerializer(page.object_list, many=True)

        return SuccessResponse(
            {
                "saf_ticket_sources": serialized.data,
                "ids": list(ids),
                "from": from_idx,
                "returned": len(serialized.data),
                "total": len(ids),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketSourceError.TICKET_SOURCE_LISTING_FAILED)


def parse_ticket_source_query(query):
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


def find_ticket_sources(**filters):
    ticket_sources = (
        SafTicketSource.objects.select_related("feedstock")
        .prefetch_related("saf_tickets")
        .prefetch_related("saf_tickets__client")
    )

    if filters["entity_id"] != None:
        ticket_sources = ticket_sources.filter(added_by_id=filters["entity_id"])

    if filters["year"] != None:
        ticket_sources = ticket_sources.filter(year=filters["year"])

    if filters["period"] != None:
        ticket_sources = ticket_sources.filter(period__in=filters["period"])

    if filters["feedstock"] != None:
        ticket_sources = ticket_sources.filter(feedstock__code__in=filters["feedstock"])

    if filters["client"] != None:
        ticket_sources = ticket_sources.filter(saf_tickets__client__name__in=filters["client"])

    if filters["status"] == "available":
        ticket_sources = ticket_sources.filter(assigned_volume__lt=F("total_volume"))
    elif filters["status"] == "history":
        ticket_sources = ticket_sources.filter(assigned_volume__gte=F("total_volume"))
    else:
        raise Exception("Status '%s' does not exist for ticket sources" % filters["status"])

    return ticket_sources
