from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from .provision_certificates import ProvisionCertificatesFilterForm, find_provision_certificates


class CertificateFilterError:
    BAD_FILTER = "BAD_FILTER"


@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_provision_certificate_filters(request):
    filters = ProvisionCertificatesFilterForm(request.GET)
    current_filter = request.GET.get("filter")

    if not filters.is_valid():
        return ErrorResponse(400, CertificateFilterError.BAD_FILTER, filters.errors)

    if current_filter == "status":
        return SuccessResponse({"filter_values": ["FULL", "AVAILABLE", "EMPTY"]})

    filters.cleaned_data[current_filter] = None
    provision_certificates = find_provision_certificates(**filters.cleaned_data)

    remaining_filter_values = provision_certificates.values_list(filter_to_column[current_filter], flat=True).distinct()

    return SuccessResponse({"filter_values": list(remaining_filter_values)})


filter_to_column = {
    "year": "year",
    "status": "status",
    "quarter": "quarter",
    "cpo": "cpo__name",
    "operating_unit": "operating_unit",
}