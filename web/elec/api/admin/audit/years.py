import traceback

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from core.utils import combine
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication


@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_years(request):
    try:
        charge_points_years = ElecChargePointApplication.objects.values_list("created_at__year", flat=True).distinct()
        meter_readings_years = ElecMeterReadingApplication.objects.values_list("year", flat=True).distinct()

        years = combine(charge_points_years, meter_readings_years)
        return SuccessResponse(years)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CarbureError.UNKNOWN_ERROR)
