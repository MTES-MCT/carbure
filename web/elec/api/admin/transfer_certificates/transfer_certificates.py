import csv
import datetime
import traceback
from math import floor

from django import forms
from django.core.paginator import Paginator
from django.http import HttpResponse

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.excel import export_to_excel
from core.models import ExternalAdminRights
from core.utils import MultipleValueField
from elec.models.elec_transfer_certificate import ElecTransferCertificate
from elec.serializers.elec_transfer_certificate import ElecTransferCertificateSerializer


class TransferCertificatesError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    TRANSFER_CERTIFICATES_LISTING_FAILED = "TRANSFER_CERTIFICATES_LISTING_FAILED"


class TransferCertificatesFilterForm(forms.Form):
    year = forms.IntegerField()
    status = MultipleValueField(coerce=str, required=False)
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

    export = "export" in request.GET

    sort_by = transf_certif_sort_form.cleaned_data["sort_by"]
    order = transf_certif_sort_form.cleaned_data["order"]
    from_idx = transf_certif_sort_form.cleaned_data["from_idx"] or 0
    limit = transf_certif_sort_form.cleaned_data["limit"] or 25

    try:
        transfer_certificates = ElecTransferCertificate.objects.all()
        transfer_certificates = find_transfer_certificates(transfer_certificates, **transf_certif_filter_form.cleaned_data)
        transfer_certificates = sort_transfer_certificates(transfer_certificates, sort_by, order)

        if export:
            return export_transfer_certificate_to_csv(transfer_certificates)

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
    transfer_certificates = transfer_certificates.select_related("supplier", "client")

    if filters["year"]:
        transfer_certificates = transfer_certificates.filter(transfer_date__year=filters["year"])

    if filters["status"]:
        transfer_certificates = transfer_certificates.filter(status__in=filters["status"])

    if filters["transfer_date"]:
        transfer_certificates = transfer_certificates.filter(transfer_date__in=filters["transfer_date"])

    if filters["cpo"]:
        transfer_certificates = transfer_certificates.filter(supplier__name__in=filters["cpo"])

    if filters["operator"]:
        transfer_certificates = transfer_certificates.filter(client__name__in=filters["operator"])

    return transfer_certificates


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


def export_transfer_certificate_to_csv(transfer_certificates):
    today = datetime.date.today()
    file = "carbure_elec_transfer_certificate_%s.csv" % (today.strftime("%Y%m%d_%H%M"))

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{file}"'},
    )

    writer = csv.writer(response)

    columns = ["certificate_id", "status", "supplier", "client", "transfer_date", "energy_amount"]
    writer.writerow(columns)

    for pc in transfer_certificates:
        serialized = [
            pc.certificate_id,
            pc.status,
            pc.supplier.name,
            pc.client.name,
            pc.transfer_date,
            pc.energy_amount,
        ]
        writer.writerow(serialized)

    return response


def export_transfer_certificate_to_excel(transfer_certificates):
    today = datetime.date.today()
    file = "carbure_elec_transfer_certificate_%s.xlsx" % (today.strftime("%Y%m%d_%H%M"))

    return export_to_excel(
        file,
        [
            {
                "label": "tickets",
                "rows": ElecTransferCertificateSerializer(transfer_certificates, many=True).data,
                "columns": [
                    {"label": "certificate_id", "value": "certificate_id"},
                    {"label": "supplier", "value": "supplier.name"},
                    {"label": "client", "value": "client.name"},
                    {"label": "transfer_date", "value": "transfer_date"},
                    {"label": "energy_amount", "value": "energy_amount"},
                ],
            }
        ],
    )
