from math import floor
import traceback

from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from elec.models.elec_provision_certificate import ElecProvisionCertificate
from elec.serializers.elec_provision_certificate import ElecProvisionCertificateSerializer

from admin.api.elec.provision_certificates import (
    ProvisionCertificatesError,
    ProvisionCertificatesFilterForm,
    ProvisionCertificatesSortForm,
    find_provision_certificates,
    sort_provision_certificates,
)


@require_GET
@check_user_rights()
def get_provision_certificates(request):
    prov_certif_filter_form = ProvisionCertificatesFilterForm(request.GET)
    prov_certif_sort_form = ProvisionCertificatesSortForm(request.GET)

    if not prov_certif_filter_form.is_valid() or not prov_certif_sort_form.is_valid():
        return ErrorResponse(
            400,
            ProvisionCertificatesError.MALFORMED_PARAMS,
            {**prov_certif_filter_form.errors, **prov_certif_sort_form.errors},
        )

    entity_id = request.GET.get("entity_id")
    sort_by = prov_certif_sort_form.cleaned_data["sort_by"]
    order = prov_certif_sort_form.cleaned_data["order"]
    from_idx = prov_certif_sort_form.cleaned_data["from_idx"]
    limit = prov_certif_sort_form.cleaned_data["limit"]

    try:
        provision_certificates = ElecProvisionCertificate.objects.filter(cpo_id=entity_id)
        provision_certificates = find_provision_certificates(**prov_certif_filter_form.cleaned_data)
        provision_certificates = sort_provision_certificates(provision_certificates, sort_by, order)

        paginator = Paginator(provision_certificates, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)

        ids = provision_certificates.values_list("id", flat=True)
        serialized = ElecProvisionCertificateSerializer(page.object_list, many=True)

        return SuccessResponse(
            {
                "elec_provision_certificates": serialized.data,
                "ids": list(ids),
                "from": from_idx,
                "returned": len(serialized.data),
                "total": len(ids),
            }
        )

    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ProvisionCertificatesError.PROVISION_CERTIFICATES_LISTING_FAILED)
