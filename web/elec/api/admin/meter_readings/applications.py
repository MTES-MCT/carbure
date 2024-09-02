from django import forms
from django.views.decorators.http import require_GET

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import Entity, ExternalAdminRights
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.serializers.elec_meter_reading_application import ElecMeterReadingApplicationSerializer


class ApplicationsForm(forms.Form):
    company_id = forms.ModelChoiceField(queryset=Entity.objects.filter(entity_type=Entity.CPO))


class ApplicationsError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_applications(request):
    form = ApplicationsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, ApplicationsError.MALFORMED_PARAMS, form.errors)

    company = form.cleaned_data["company_id"]

    applications = MeterReadingRepository.get_annotated_applications_by_cpo(company)
    serialized = ElecMeterReadingApplicationSerializer(applications, many=True).data
    return SuccessResponse(serialized)
