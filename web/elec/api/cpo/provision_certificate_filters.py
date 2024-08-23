from django.views.decorators.http import require_GET

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from elec.api.admin.transfer_certificates.transfer_certificate_filters import CertificateFilterError
from elec.models.elec_provision_certificate import ElecProvisionCertificate

from .provision_certificates import ProvisionCertificatesFilterForm, find_provision_certificates


@require_GET
@check_user_rights()
def get_provision_certificate_filters(request, *args, **kwargs):
    filters = ProvisionCertificatesFilterForm(request.GET)

    if not filters.is_valid():
        return ErrorResponse(400, CertificateFilterError.BAD_FILTER, filters.errors)

    entity_id = request.GET.get("entity_id")
    current_filter = request.GET.get("filter")

    if current_filter == "status":
        return SuccessResponse({"filter_values": ["FULL", "HISTORY"]})

    filters.cleaned_data[current_filter] = None

    provision_certificates = ElecProvisionCertificate.objects.filter(cpo_id=entity_id)
    provision_certificates = find_provision_certificates(provision_certificates, **filters.cleaned_data)

    remaining_filter_values = provision_certificates.values_list(filter_to_column[current_filter], flat=True).distinct()

    return SuccessResponse({"filter_values": list(remaining_filter_values)})


filter_to_column = {
    "year": "year",
    "status": "status",
    "quarter": "quarter",
    "cpo": "cpo__name",
    "operating_unit": "operating_unit",
}
