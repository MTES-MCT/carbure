import traceback
from math import floor

from django.core.paginator import Paginator
from django.views.decorators.http import require_GET

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from elec.api.admin.transfer_certificates.transfer_certificates import (
    TransferCertificatesError,
    TransferCertificatesFilterForm,
    TransferCertificatesSortForm,
    export_transfer_certificate_to_excel,
    find_transfer_certificates,
    sort_transfer_certificates,
)
from elec.models.elec_transfer_certificate import ElecTransferCertificate
from elec.serializers.elec_transfer_certificate import ElecTransferCertificateSerializer


@require_GET
@check_user_rights()
def get_transfer_certificates(request, *args, **kwargs):
    transf_certif_filter_form = TransferCertificatesFilterForm(request.GET)
    transf_certif_sort_form = TransferCertificatesSortForm(request.GET)

    if not transf_certif_filter_form.is_valid() or not transf_certif_sort_form.is_valid():
        return ErrorResponse(
            400,
            TransferCertificatesError.MALFORMED_PARAMS,
            {**transf_certif_filter_form.errors, **transf_certif_sort_form.errors},
        )

    export = "export" in request.GET

    entity_id = request.GET.get("entity_id")
    sort_by = transf_certif_sort_form.cleaned_data["sort_by"]
    order = transf_certif_sort_form.cleaned_data["order"]
    from_idx = transf_certif_sort_form.cleaned_data["from_idx"] or 0
    limit = transf_certif_sort_form.cleaned_data["limit"] or 25

    try:
        transfer_certificates = ElecTransferCertificate.objects.filter(client_id=entity_id)
        transfer_certificates = find_transfer_certificates(transfer_certificates, **transf_certif_filter_form.cleaned_data)
        transfer_certificates = sort_transfer_certificates(transfer_certificates, sort_by, order)

        if export:
            file = export_transfer_certificate_to_excel(transfer_certificates)
            return ExcelResponse(file)

        paginator = Paginator(transfer_certificates, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)

        ids = transfer_certificates.values_list("id", flat=True)
        serialized = ElecTransferCertificateSerializer(page.object_list, many=True)

        return SuccessResponse(
            {
                "elec_transfer_certificates": serialized.data,
                "ids": list(ids),
                "from": from_idx,
                "returned": len(serialized.data),
                "total": len(ids),
            }
        )

    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, TransferCertificatesError.TRANSFER_CERTIFICATES_LISTING_FAILED)
