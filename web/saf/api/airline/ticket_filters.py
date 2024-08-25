# /api/saf/airline/tickets/filters

import traceback

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights

from .tickets import find_tickets, parse_ticket_query


class SafTicketFiltersError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    FILTER_LISTING_FAILED = "FILTERS_LISTING_FAILED"


@check_user_rights()
def get_ticket_filters(request, *args, **kwargs):
    try:
        query = parse_ticket_query(request.GET)
        filter = request.GET.get("filter")
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketFiltersError.MALFORMED_PARAMS)

    try:
        # do not apply the filter we are listing so we can get all its possible values in the current context
        query[filter] = None
        # find all ticket sources matching the rest of the query
        tickets = find_tickets(**query)
        # get the available values for the selected filter
        data = get_filter_values(tickets, filter)

        return SuccessResponse(list(set(data)))
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketFiltersError.FILTER_LISTING_FAILED)


def get_filter_values(tickets, filter):
    if not filter:
        raise Exception("No filter was specified")

    if filter == "suppliers":
        column = "supplier__name"
    elif filter == "periods":
        column = "assignment_period"
    elif filter == "feedstocks":
        column = "feedstock__code"
    else:  # raise an error for unknown filters
        raise Exception("Filter '%s' does not exist for tickets" % filter)

    values = tickets.values_list(column, flat=True).distinct()
    return [v for v in values if v]
