# /api/v5/saf/operator/ticket-sources

from math import floor
import traceback
from django.core.paginator import Paginator
from django.db.models.expressions import F
from django.db.models import Q

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
        sort_by = request.GET.get("sort_by")
        order = request.GET.get("order")
        from_idx = int(request.GET.get("from_idx", 0))
        limit = int(request.GET.get("limit", 25))
    except:
        return ErrorResponse(400, SafTicketSourceError.MALFORMED_PARAMS)

    try:
        ticket_sources = find_ticket_sources(**query)
        ticket_sources = sort_ticket_sources(ticket_sources, sort_by, order)

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
    search = query.get("search", None)
    periods = [int(p) for p in query.getlist("periods")] if "periods" in query else None
    clients = query.getlist("clients") if "clients" in query else None
    feedstocks = query.getlist("feedstocks") if "feedstocks" in query else None

    return {
        "entity_id": entity_id,
        "status": status,
        "year": year,
        "periods": periods,
        "feedstocks": feedstocks,
        "clients": clients,
        "search": search,
    }


def find_ticket_sources(**filters):
    ticket_sources = (
        SafTicketSource.objects.select_related("feedstock", "biofuel", "country_of_origin", "carbure_production_site")
        .prefetch_related("saf_tickets")
        .prefetch_related("saf_tickets__client")
    )

    if filters["entity_id"] != None:
        ticket_sources = ticket_sources.filter(added_by_id=filters["entity_id"])

    if filters["year"] != None:
        ticket_sources = ticket_sources.filter(year=filters["year"])

    if filters["periods"] != None:
        ticket_sources = ticket_sources.filter(delivery_period__in=filters["periods"])

    if filters["feedstocks"] != None:
        ticket_sources = ticket_sources.filter(feedstock__code__in=filters["feedstocks"])

    if filters["clients"] != None:
        ticket_sources = ticket_sources.filter(saf_tickets__client__name__in=filters["clients"])

    if filters["status"] == "AVAILABLE":
        ticket_sources = ticket_sources.filter(assigned_volume__lt=F("total_volume"))
    elif filters["status"] == "HISTORY":
        ticket_sources = ticket_sources.filter(assigned_volume__gte=F("total_volume"))
    else:
        raise Exception("Status '%s' does not exist for ticket sources" % filters["status"])

    if filters["search"] != None:
        ticket_sources = ticket_sources.filter(
            Q(carbure_id__icontains=filters["search"])
            | Q(saf_tickets__client__name__icontains=filters["search"])
            | Q(feedstock__name__icontains=filters["search"])
            | Q(biofuel__name__icontains=filters["search"])
            | Q(country_of_origin__name__icontains=filters["search"])
            | Q(carbure_production_site__name__icontains=filters["search"])
            | Q(unknown_production_site__icontains=filters["search"])
        )

    return ticket_sources


def sort_ticket_sources(ticket_sources, sort_by, order):
    sortable_columns = {
        "volume": "total_volume",
        "period": "delivery_period",
        "feedstock": "feedstock__code",
        "ghg_reduction": "ghg_reduction",
    }

    column = sortable_columns.get(sort_by, "created_at")

    if order == "desc":
        return ticket_sources.order_by("-%s" % column)
    else:
        return ticket_sources.order_by(column)
