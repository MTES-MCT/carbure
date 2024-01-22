import traceback
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from elec.api.cpo import meter_readings
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.models.elec_provision_certificate import ElecProvisionCertificate
from elec.models.elec_transfer_certificate import ElecTransferCertificate


@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_years(request):
    try:
        charging_points_years = ElecChargePointApplication.objects.values_list("created_at__year", flat=True).distinct()
        meter_readings_years = ElecMeterReadingApplication.objects.values_list("year", flat=True).distinct()

        years = list(set(list(charging_points_years) + list(meter_readings_years)))

        return SuccessResponse(list(years))
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CarbureError.UNKNOWN_ERROR)
