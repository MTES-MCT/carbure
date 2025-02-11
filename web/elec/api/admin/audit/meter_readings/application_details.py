from django import forms
from django.views.decorators.http import require_GET

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.serializers.elec_meter_reading_application import ElecMeterReadingApplicationDetailsSerializer


class ApplicationDetailsForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=MeterReadingRepository.get_annotated_applications_details())
    export = forms.BooleanField(required=False)


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_application_details(request):
    form = ApplicationDetailsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application = form.cleaned_data["application_id"]
    charge_point_application = ElecMeterReadingApplicationDetailsSerializer(application).data
    return SuccessResponse(charge_point_application)
