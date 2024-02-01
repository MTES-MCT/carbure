import traceback
from django import forms
from django.db.models import Sum
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.models.elec_provision_certificate import ElecProvisionCertificate
from elec.models.elec_transfer_certificate import ElecTransferCertificate


class ElecAuditSnapshotForm(forms.Form):
    year = forms.IntegerField()


@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_snapshot(request):
    snapshot_form = ElecAuditSnapshotForm(request.GET)

    if not snapshot_form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, snapshot_form.errors)

    year = snapshot_form.cleaned_data["year"]

    try:
        charge_points_applications = ElecChargePointApplication.objects.filter(created_at__year=year)
        meter_readings_applications = ElecMeterReadingApplication.objects.filter(year=year)

        return SuccessResponse(
            {
                "charge_points_applications": charge_points_applications.count(),
                "charge_points_applications_pending": charge_points_applications.filter(
                    status__in=[ElecChargePointApplication.PENDING, ElecChargePointApplication.AUDIT_IN_PROGRESS]
                ).count(),
                "charge_points_applications_history": charge_points_applications.filter(
                    status__in=[ElecChargePointApplication.REJECTED, ElecChargePointApplication.ACCEPTED]
                ).count(),
                "meter_readings_applications": meter_readings_applications.count(),
                "meter_readings_applications_pending": meter_readings_applications.filter(
                    status__in=[ElecMeterReadingApplication.PENDING, ElecMeterReadingApplication.AUDIT_IN_PROGRESS]
                ).count(),
                "meter_readings_applications_history": meter_readings_applications.filter(
                    status__in=[ElecMeterReadingApplication.REJECTED, ElecMeterReadingApplication.ACCEPTED]
                ).count(),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CarbureError.UNKNOWN_ERROR)
