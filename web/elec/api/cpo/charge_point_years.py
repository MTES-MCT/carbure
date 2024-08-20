import traceback
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from django.views.decorators.http import require_GET
from core.utils import combine
from core.decorators import check_user_rights
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication


@require_GET
@check_user_rights()
def get_charge_point_years(request, *args, **kwargs):
    entity_id = request.GET.get("entity_id")

    try:
        charge_points_years = (
            ElecChargePointApplication.objects.filter(cpo_id=entity_id).values_list("created_at__year", flat=True).distinct()
        )
        meter_readings_years = (
            ElecMeterReadingApplication.objects.filter(cpo_id=entity_id).values_list("year", flat=True).distinct()
        )

        years = combine(charge_points_years, meter_readings_years)
        return SuccessResponse(years)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CarbureError.UNKNOWN_ERROR)
