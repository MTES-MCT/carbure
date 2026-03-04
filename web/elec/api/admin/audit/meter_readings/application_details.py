from django import forms
from django.db.models import Prefetch
from django.views.decorators.http import require_GET

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from elec.models.elec_audit_charge_point import ElecAuditChargePoint
from elec.models.elec_audit_sample import ElecAuditSample
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.serializers.elec_meter_reading_application import ElecMeterReadingApplicationDetailsSerializer


class ApplicationDetailsForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ElecMeterReadingApplication.objects.all())
    export = forms.BooleanField(required=False)


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_application_details(request):
    form = ApplicationDetailsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application_id = form.cleaned_data["application_id"].pk

    # Prefetch the audited charge points and the current meter to avoid N+1 queries
    audited_charge_points_prefetch = Prefetch(
        "audited_charge_points",
        queryset=ElecAuditChargePoint.objects.select_related("charge_point", "charge_point__current_meter"),
    )

    audit_sample_prefetch = Prefetch(
        "audit_sample",
        queryset=ElecAuditSample.objects.prefetch_related(audited_charge_points_prefetch),
    )

    application = ElecMeterReadingApplication.objects.prefetch_related(audit_sample_prefetch).get(id=application_id)

    # Append annotated data to the application
    application = MeterReadingRepository.get_annotated_applications_details(application)

    charge_point_application = ElecMeterReadingApplicationDetailsSerializer(application).data
    return SuccessResponse(charge_point_application)
