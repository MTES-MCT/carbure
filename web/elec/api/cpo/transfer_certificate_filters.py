from django.views.decorators.http import require_GET
from admin.api.elec.transfer_certificate_filters import CertificateFilterError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights, check_user_rights
from core.models import ExternalAdminRights
from elec.models.elec_transfer_certificate import ElecTransferCertificate
from .transfer_certificates import TransferCertificatesFilterForm, find_transfer_certificates


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_transfer_certificate_filters(request):
    filters = TransferCertificatesFilterForm(request.GET)

    if not filters.is_valid():
        return ErrorResponse(400, CertificateFilterError.BAD_FILTER, filters.errors)

    entity_id = request.GET.get("entity_id")
    current_filter = request.GET.get("filter")

    filters.cleaned_data[current_filter] = None

    transfer_certificates = ElecTransferCertificate.objects.filter(supplier_id=entity_id)
    transfer_certificates = find_transfer_certificates(transfer_certificates, **filters.cleaned_data)

    remaining_filter_values = transfer_certificates.values_list(filter_to_column[current_filter], flat=True).distinct()

    return SuccessResponse({"filter_values": list(remaining_filter_values)})


filter_to_column = {
    "year": "transfer_date__year",
    "cpo": "supplier__name",
    "operator": "client__name",
    "certificate_id": "certificate_id",
}
