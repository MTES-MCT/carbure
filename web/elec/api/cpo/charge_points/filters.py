from django.db.models.expressions import OuterRef, Subquery

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.models import ElecChargePoint, ElecMeterReading

from .charge_points import ChargePointFilterForm, filter_charge_points


class ChargePointFilterError:
    BAD_FILTER = "BAD_FILTER"


@check_user_rights(entity_type=[Entity.CPO])
def get_charge_points_filters(request, entity):
    filters = ChargePointFilterForm(request.GET)
    current_filter = request.GET.get("filter")

    if not filters.is_valid():
        return ErrorResponse(400, ChargePointFilterError.BAD_FILTER, filters.errors)

    if current_filter == "status":
        return SuccessResponse({"filter_values": ["AVAILABLE", "HISTORY"]})

    filters.cleaned_data[current_filter] = None

    charge_points = ElecChargePoint.objects.filter(cpo=entity)
    charge_points = filter_charge_points(charge_points, **filters.cleaned_data)
    charge_points = charge_points.select_related("application")

    if current_filter == "last_index":
        latest_reading_subquery = (
            ElecMeterReading.objects.filter(charge_point=OuterRef("pk")).order_by("-reading_date").values("pk")[:1]
        )
        charge_points_with_latest_reading = charge_points.annotate(latest_reading_id=Subquery(latest_reading_subquery))
        remaining_filter_values = (
            ElecMeterReading.objects.filter(pk__in=charge_points_with_latest_reading.values("latest_reading_id"))
            .values_list("extracted_energy")
            .order_by("extracted_energy")
            .distinct()
        )
    else:
        remaining_filter_values = charge_points.values_list(filter_to_column[current_filter], flat=True).distinct()

    return SuccessResponse({"filter_values": list(remaining_filter_values)})


filter_to_column = {
    "status": "status",
    "created_at": "application__created_at",
    "charge_point_id": "charge_point_id",
    "last_index": "last_index",
    "is_article_2": "application__is_article_2",
}
