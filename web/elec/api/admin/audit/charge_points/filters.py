# /api/saf/operator/ticket-sources/filters

import traceback
from django import forms
from django.db.models.functions import Coalesce
from core.carburetypes import CarbureError
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from elec.api.admin.audit.charge_points.applications import AuditApplicationsFilterForm, filter_charge_point_applications
from elec.repositories.charge_point_repository import ChargePointRepository


class SafTicketSourceFiltersError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    FILTER_LISTING_FAILED = "FILTERS_LISTING_FAILED"


@check_user_rights()
def get_charge_points_applications_filters(request, *args, **kwargs):
    filter_form = AuditApplicationsFilterForm(request.GET)

    if not filter_form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, filter_form.errors)

    filter = request.GET.get("filter")
    query = filter_form.cleaned_data

    try:
        # do not apply the filter we are listing so we can get all its possible values in the current context
        query[filter] = None
        charge_points_applications = ChargePointRepository.get_annotated_applications()
        # find all applications  matching the rest of the query
        charge_points_applications = filter_charge_point_applications(charge_points_applications, **query)
        # get the available values for the selected filter
        data = get_filter_values(charge_points_applications, filter)

        return SuccessResponse(list(set(data)))
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketSourceFiltersError.FILTER_LISTING_FAILED)


def get_filter_values(applications, filter):
    if not filter:
        raise Exception("No filter was specified")

    if filter == "cpo":
        column = "cpo__name"

    else:  # raise an error for unknown filters
        raise Exception("Filter '%s' does not exist for ticket sources" % filter)

    # ticket_sources = ticket_sources.annotate(
    #     parent_supplier=Coalesce(
    #         "parent_lot__carbure_supplier__name",
    #         "parent_lot__unknown_supplier",
    #         "parent_ticket__supplier__name",
    #     )
    # )

    values = applications.values_list(column, flat=True).distinct()
    return [v for v in values if v]
