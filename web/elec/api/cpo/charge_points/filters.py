from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.models import ElecChargePoint

from .charge_points import ChargePointFilterForm, annotate_with_latest_meter_reading_date, filter_charge_points


class ChargePointFilterError:
    BAD_FILTER = "BAD_FILTER"


@check_user_rights(entity_type=[Entity.CPO])
def get_charge_points_filters(request, entity):
    filters = ChargePointFilterForm(request.GET)
    current_filter = request.GET.get("filter")

    if not filters.is_valid():
        return ErrorResponse(400, ChargePointFilterError.BAD_FILTER, filters.errors)

    if current_filter == "status":
        return SuccessResponse({"filter_values": ["PENDING", "AUDIT_IN_PROGRESS", "ACCEPTED"]})

    filters.cleaned_data[current_filter] = None

    charge_points = ElecChargePoint.objects.filter(cpo=entity, is_deleted=False)
    charge_points = filter_charge_points(charge_points, **filters.cleaned_data)
    charge_points = charge_points.select_related("application")

    if current_filter == "latest_meter_reading_month":
        charge_points = annotate_with_latest_meter_reading_date(charge_points)

    remaining_filter_values = charge_points.values_list(filter_to_column[current_filter], flat=True).distinct()

    if current_filter == "latest_meter_reading_month":
        remaining_filter_values = {f"{date.month}/{date.year}" if date else "null" for date in remaining_filter_values}

    return SuccessResponse({"filter_values": list(remaining_filter_values)})


filter_to_column = {
    "status": "status",
    "application_date": "application__created_at",
    "charge_point_id": "charge_point_id",
    "station_id": "station_id",
    "latest_meter_reading_month": "latest_meter_reading_date",
    "is_article_2": "application__is_article_2",
}
