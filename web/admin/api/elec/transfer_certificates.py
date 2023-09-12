from math import floor
import traceback

from django import forms
from django.core.paginator import Paginator
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from core.utils import MultipleValueField
from elec.models.elec_transfer_certificate import ElecTransferCertificate
from elec.serializers.elec_transfer_certificate import ElecTransferCertificateSerializer


class TransferCertificatesError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    TRANSFER_CERTIFICATES_LISTING_FAILED = "TRANSFER_CERTIFICATES_LISTING_FAILED"


class TransferCertificatesFilterForm(forms.Form):
    year = forms.IntegerField()
    transfer_date = MultipleValueField(coerce=str, required=False)
    cpo = MultipleValueField(coerce=str, required=False)
    operator = MultipleValueField(coerce=str, required=False)
    certificate_id = MultipleValueField(coerce=str, required=False)


class TransferCertificatesSortForm(forms.Form):
    sort_by = forms.CharField(required=False)
    order = forms.CharField(required=False)
    from_idx = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_transfer_certificates(request):
    transf_certif_filter_form = TransferCertificatesFilterForm(request.GET)
    transf_certif_sort_form = TransferCertificatesSortForm(request.GET)

    if not transf_certif_filter_form.is_valid() or not transf_certif_sort_form.is_valid():
        return ErrorResponse(
            400,
            TransferCertificatesError.MALFORMED_PARAMS,
            {**transf_certif_filter_form.errors, **transf_certif_sort_form.errors},
        )

    sort_by = transf_certif_sort_form.cleaned_data["sort_by"]
    order = transf_certif_sort_form.cleaned_data["order"]
    from_idx = transf_certif_sort_form.cleaned_data["from_idx"] or 0
    limit = transf_certif_sort_form.cleaned_data["limit"] or 25

    try:
        transfer_certificates = ElecTransferCertificate.objects.all()
        transfer_certificates = find_transfer_certificates(transfer_certificates, **transf_certif_filter_form.cleaned_data)
        transfer_certificates = sort_transfer_certificates(transfer_certificates, sort_by, order)

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


def find_transfer_certificates(transfer_certificates, **filters):
    transfer_certificate = transfer_certificates.select_related("supplier", "client")

    if filters["year"]:
        transfer_certificate = transfer_certificate.filter(transfer_date__year=filters["year"])

    if filters["transfer_date"]:
        transfer_certificate = transfer_certificate.filter(transfer_date__in=filters["transfer_date"])

    if filters["cpo"]:
        transfer_certificate = transfer_certificate.filter(supplier__name__in=filters["cpo"])

    if filters["operator"]:
        transfer_certificate = transfer_certificate.filter(client__name__in=filters["operator"])

    return transfer_certificate


def sort_transfer_certificates(transfer_certificates, sort_by, order):
    sortable_columns = {
        "transfer_date": "transfer_date",
        "energy_amount": "energy_amount",
        "cpo": "supplier__name",
        "operator": "client__name",
    }

    column = sortable_columns.get(sort_by, "id")

    if order == "desc":
        return transfer_certificates.order_by("-%s" % column)
    else:
        return transfer_certificates.order_by(column)
