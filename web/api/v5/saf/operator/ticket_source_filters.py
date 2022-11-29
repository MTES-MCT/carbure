# /api/v5/saf/operator/ticket-sources/filters

import traceback
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from .ticket_sources import parse_ticket_source_query, find_ticket_sources


class SafTicketSourceFiltersError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    FILTER_LISTING_FAILED = "FILTERS_LISTING_FAILED"


@check_user_rights()
def get_ticket_source_filters(request, *args, **kwargs):
    try:
        query = parse_ticket_source_query(request.GET)
        filter = request.GET.get("filter")
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketSourceFiltersError.MALFORMED_PARAMS)

    try:
        # do not apply the filter we are listing so we can get all its possible values in the current context
        query[filter] = None
        # find all ticket sources matching the rest of the query
        ticket_sources = find_ticket_sources(**query)
        # get the available values for the selected filter
        data = get_filter_values(ticket_sources, filter)

        return SuccessResponse(list(set(data)))
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketSourceFiltersError.FILTER_LISTING_FAILED)


def get_filter_values(ticket_sources, filter):
    if not filter:
        raise Exception("No filter was specified")

    if filter == "clients":
        column = "saf_tickets__client__name"
    elif filter == "periods":
        column = "delivery_period"
    elif filter == "feedstocks":
        column = "feedstock__code"
    else:  # raise an error for unknown filters
        raise Exception("Filter '%s' does not exist for ticket sources" % filter)

    values = ticket_sources.values_list(column, flat=True).distinct()
    return [v for v in values if v]
