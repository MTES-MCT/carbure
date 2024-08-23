# /api/saf/operator/ticket-sources/filters

import traceback

from django.db.models.functions import Coalesce

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights

from .ticket_sources import TicketSourceFilterForm, find_ticket_sources


class SafTicketSourceFiltersError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    FILTER_LISTING_FAILED = "FILTERS_LISTING_FAILED"


@check_user_rights()
def get_ticket_source_filters(request, *args, **kwargs):
    filter_form = TicketSourceFilterForm(request.GET)

    if not filter_form.is_valid():
        return ErrorResponse(400, SafTicketSourceFiltersError.MALFORMED_PARAMS, filter_form.errors)

    filter = request.GET.get("filter")
    query = filter_form.cleaned_data

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
    elif filter == "countries_of_origin":
        column = "country_of_origin__code_pays"
    elif filter == "production_sites":
        column = "carbure_production_site__name"
    elif filter == "delivery_sites":
        column = "parent_lot__carbure_delivery_site__name"
    elif filter == "suppliers":
        column = "parent_supplier"

    else:  # raise an error for unknown filters
        raise Exception("Filter '%s' does not exist for ticket sources" % filter)

    ticket_sources = ticket_sources.annotate(
        parent_supplier=Coalesce(
            "parent_lot__carbure_supplier__name",
            "parent_lot__unknown_supplier",
            "parent_ticket__supplier__name",
        )
    )

    values = ticket_sources.values_list(column, flat=True).distinct()
    return [v for v in values if v]
