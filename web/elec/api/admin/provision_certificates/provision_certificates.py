import csv
import datetime
import traceback
from math import floor

from django import forms
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from core.utils import MultipleValueField
from elec.models.elec_provision_certificate import ElecProvisionCertificate
from elec.serializers.elec_provision_certificate import ElecProvisionCertificateSerializer


class ProvisionCertificatesError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    PROVISION_CERTIFICATES_LISTING_FAILED = "PROVISION_CERTIFICATES_LISTING_FAILED"


class ProvisionCertificatesFilterForm(forms.Form):
    year = forms.IntegerField()
    status = MultipleValueField(coerce=str, required=False)
    quarter = MultipleValueField(coerce=int, required=False)
    cpo = MultipleValueField(coerce=str, required=False)
    operating_unit = MultipleValueField(coerce=str, required=False)
    search = forms.CharField(required=False)


class ProvisionCertificatesSortForm(forms.Form):
    sort_by = forms.CharField(required=False)
    order = forms.CharField(required=False)
    from_idx = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_provision_certificates(request):
    prov_certif_filter_form = ProvisionCertificatesFilterForm(request.GET)
    prov_certif_sort_form = ProvisionCertificatesSortForm(request.GET)

    if not prov_certif_filter_form.is_valid() or not prov_certif_sort_form.is_valid():
        return ErrorResponse(
            400,
            ProvisionCertificatesError.MALFORMED_PARAMS,
            {**prov_certif_filter_form.errors, **prov_certif_sort_form.errors},
        )

    export = "export" in request.GET

    sort_by = prov_certif_sort_form.cleaned_data["sort_by"]
    order = prov_certif_sort_form.cleaned_data["order"]
    from_idx = prov_certif_sort_form.cleaned_data["from_idx"] or 0
    limit = prov_certif_sort_form.cleaned_data["limit"] or 25

    try:
        provision_certificates = ElecProvisionCertificate.objects.all()
        provision_certificates = find_provision_certificates(provision_certificates, **prov_certif_filter_form.cleaned_data)
        provision_certificates = sort_provision_certificates(provision_certificates, sort_by, order)

        if export:
            return export_provision_certificate_to_csv(provision_certificates)

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


def find_provision_certificates(provision_certificates, **filters):
    provision_certificates = provision_certificates.select_related("cpo")

    if filters["year"]:
        provision_certificates = provision_certificates.filter(year=filters["year"])

    if filters["quarter"]:
        provision_certificates = provision_certificates.filter(quarter__in=filters["quarter"])

    if filters["cpo"]:
        provision_certificates = provision_certificates.filter(cpo__name__in=filters["cpo"])

    if filters["operating_unit"]:
        provision_certificates = provision_certificates.filter(operating_unit__in=filters["operating_unit"])

    if filters["status"]:
        status_filter = Q()
        if "AVAILABLE" in filters["status"]:
            status_filter = status_filter | Q(remaining_energy_amount__gt=0)
        if "HISTORY" in filters["status"]:
            status_filter = status_filter | Q(remaining_energy_amount=0)
        provision_certificates = provision_certificates.filter(status_filter)

    if filters["search"] != None:
        provision_certificates = provision_certificates.filter(
            Q(cpo__name__icontains=filters["search"]) | Q(operating_unit__icontains=filters["search"])
        )

    return provision_certificates


def sort_provision_certificates(provision_certificates, sort_by, order):
    sortable_columns = {
        "quarter": "quarter",
        "cpo": "cpo__name",
        "energy_amount": "energy_amount",
        "operating_unit": "operating_unit",
    }

    column = sortable_columns.get(sort_by, "id")

    if order == "desc":
        return provision_certificates.order_by("-%s" % column)
    else:
        return provision_certificates.order_by(column)


def export_provision_certificate_to_csv(provision_certificates):
    today = datetime.date.today()
    file = "carbure_elec_provision_certificate_%s.csv" % (today.strftime("%Y%m%d_%H%M"))

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{file}"'},
    )

    writer = csv.writer(response)

    columns = ["id", "cpo", "quarter", "year", "operating_unit", "energy_amount", "remaining_energy_amount"]
    writer.writerow(columns)

    for pc in provision_certificates:
        serialized = [
            pc.id,
            pc.cpo.name,
            pc.quarter,
            pc.year,
            pc.operating_unit,
            pc.energy_amount,
            pc.remaining_energy_amount,
        ]
        writer.writerow(serialized)

    return response
