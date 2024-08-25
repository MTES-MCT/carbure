# /api/saf/operator/ticket-sources/filters

import traceback

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from elec.api.admin.audit.charge_points.applications import AuditApplicationsFilterForm
from elec.api.admin.audit.meter_readings.applications import filter_meter_readings_applications
from elec.repositories.meter_reading_repository import MeterReadingRepository


@check_user_rights()
def get_meter_readings_applications_filters(request, *args, **kwargs):
    filter_form = AuditApplicationsFilterForm(request.GET)

    if not filter_form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, filter_form.errors)

    filter = request.GET.get("filter")
    query = filter_form.cleaned_data

    try:
        # do not apply the filter we are listing so we can get all its possible values in the current context
        query[filter] = None
        meter_readings_applications = MeterReadingRepository.get_annotated_applications()
        # find all applications  matching the rest of the query
        meter_readings_applications = filter_meter_readings_applications(meter_readings_applications, **query)
        # get the available values for the selected filter
        data = get_filter_values(meter_readings_applications, filter)

        return SuccessResponse(list(set(data)))
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CarbureError.UNKNOWN_ERROR)


def get_filter_values(applications, filter):
    if not filter:
        raise Exception("No filter was specified")

    if filter == "cpo":
        column = "cpo__name"
    elif filter == "quarter":
        column = "quarter"
    else:  # raise an error for unknown filters
        raise Exception("Filter '%s' does not exist for tickets" % filter)

    values = applications.values_list(column, flat=True).distinct()
    return [v for v in values if v]
