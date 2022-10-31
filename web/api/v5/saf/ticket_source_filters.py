# /api/v5/saf/ticket-sources/filters

import traceback
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models.saf_ticket_source import find_ticket_sources


class SafTicketSourceFiltersError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    FILTER_LISTING_FAILED = "FILTERS_LISTING_FAILED"
    ENTITY_NOT_OPERATOR = "ENTITY_NOT_OPERATOR"


@check_user_rights()
def get_ticket_source_filters(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
        status = request.GET.get("status")
        year = int(request.GET.get("year"))
        filter = request.GET.get("filter")
        period = [int(p) for p in request.GET.getlist("period")] if "period" in request.GET else None
        client = request.GET.getlist("client") if "client" in request.GET else None
        feedstock = request.GET.getlist("feedstock") if "feedstock" in request.GET else None
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketSourceFiltersError.MALFORMED_PARAMS)

    try:
        query = {
            "entity_id": entity_id,
            "year": year,
            "period": period,
            "status": status,
            "feedstock": feedstock,
            "client": client,
            filter: None,  # do not apply the filter we are listing so we can get all its possible values in the current context
        }

        ticket_sources = find_ticket_sources(**query)

        data = []
        if filter == "client":
            data = get_filter_values(ticket_sources, "saf_tickets__client__name")
        elif filter == "period":
            data = get_filter_values(ticket_sources, "period")
        elif filter == "feedstock":
            data = get_filter_values(ticket_sources, "feedstock__code")

        return SuccessResponse(list(set(data)))
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketSourceFiltersError.FILTER_LISTING_FAILED)


def get_filter_values(ticket_sources, filter):
    values = ticket_sources.values_list(filter, flat=True).distinct()
    return [v for v in values if v]
