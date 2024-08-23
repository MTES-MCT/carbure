from datetime import datetime
from typing import List

import xlsxwriter
from django import forms
from django.db.models.query_utils import Q
from django.http import JsonResponse
from django.http.response import HttpResponse, JsonResponse

from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationPublicSerializer, DoubleCountingRegistrationSerializer
from core.common import ErrorResponse
from core.decorators import check_admin_rights
from doublecount.helpers import get_quotas


class AgreementError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


class AgreementForm(forms.Form):
    year = forms.IntegerField(required=False)
    order_by = forms.CharField(required=False)
    direction = forms.CharField(required=False)


@check_admin_rights()
def get_agreements(request, *args, **kwargs):
    sort_form = AgreementForm(request.GET)
    as_excel_file = request.GET.get("as_excel_file") == "true"

    if not sort_form.is_valid():
        return ErrorResponse(400, AgreementError.MALFORMED_PARAMS, {**sort_form.errors})

    order_by = sort_form.cleaned_data["order_by"]
    direction = sort_form.cleaned_data["direction"]

    year = sort_form.cleaned_data.get("year") or datetime.now().year

    agreements_active = (
        DoubleCountingRegistration.objects.filter(Q(valid_from__year__lte=year) & Q(valid_until__year__gte=year))
        .select_related("production_site")
        .order_by("production_site__name")
    )

    agreements_active = sort_agreements(agreements_active, order_by, direction)

    if as_excel_file:
        file_location = export_agreements(agreements_active)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response["Content-Disposition"] = 'attachment; filename="%s"' % (file_location)
        return response
    else:
        agreements_incoming = DoubleCountingRegistration.objects.filter(Q(valid_from__year__gt=year)).select_related(
            "production_site"
        )
        agreements_expired = DoubleCountingRegistration.objects.filter(Q(valid_until__year__lt=year)).select_related(
            "production_site"
        )

        active_agreements = DoubleCountingRegistrationSerializer(agreements_active, many=True).data
        active_agreements_with_quotas = add_quotas_to_agreements(year, active_agreements)

        data = {
            "active": active_agreements_with_quotas,
            "incoming": DoubleCountingRegistrationSerializer(agreements_incoming, many=True).data,
            "expired": DoubleCountingRegistrationSerializer(agreements_expired, many=True).data,
        }
        return JsonResponse({"status": "success", "data": data})


def add_quotas_to_agreements(year: int, agreements):
    quotas = get_quotas(year)
    # add quotas to active agreements
    for agreement in agreements:
        found_quotas = [q for q in quotas if q["certificate_id"] == agreement["certificate_id"]]
        agreement["quotas_progression"] = round(found_quotas[0]["quotas_progression"], 2) if len(found_quotas) > 0 else None

    return agreements


def sort_agreements(agreements, order_by, direction):
    sortable_columns = {
        "production_site": "production_site__name",
        "valid_until": "valid_until",
    }

    column = sortable_columns.get(order_by, "production_site__name")

    if direction == "desc":
        return agreements.order_by("-%s" % column)
    else:
        return agreements.order_by(column)


def export_agreements(agreements: List[DoubleCountingRegistration]):
    active_agreements = DoubleCountingRegistrationPublicSerializer(agreements, many=True).data

    today = datetime.now()
    location = "/tmp/active_agreements_%s.xlsx" % (today.strftime("%Y%m%d_%H%M"))
    workbook = xlsxwriter.Workbook(location)
    worksheet = workbook.add_worksheet("Agréments Double comptage")

    # header
    title1 = "Liste des unités de production de biocarburants reconnues au titre du décret n° 2019-570 du 7 juin 2019 portant sur la taxe incitative relative à l'incorporation des biocarburants"
    title_format = workbook.add_format({"align": "center", "valign": "vcenter", "bold": True, "border": 1})
    worksheet.merge_range("A1:H1", title1, title_format)

    title2 = "Dernière mise à jour : le " + today.strftime("%d/%m/%Y")
    worksheet.merge_range("A2:H2", title2, title_format)

    wrap_format = workbook.add_format({"text_wrap": True, "align": "center", "valign": "vcenter", "border": 1})
    worksheet.set_column("A:A", 30, cell_format=wrap_format)  # site de production

    worksheet.set_column("B:B", 30, cell_format=wrap_format)  # address
    worksheet.set_column("C:C", 10, cell_format=wrap_format)  # address
    worksheet.set_column("D:D", 10, cell_format=wrap_format)  # city
    worksheet.set_column("E:E", 10, cell_format=wrap_format)  # postal code

    worksheet.set_column("F:F", 15, cell_format=wrap_format)  # registration number
    worksheet.set_column("G:G", 20, cell_format=wrap_format)  # validity date
    worksheet.set_column("H:H", 30, cell_format=wrap_format)  # biofuels

    worksheet.merge_range("A3:A4", "Unité de production de biocarburant", cell_format=wrap_format)
    worksheet.merge_range("B3:E3", "Adresse", cell_format=wrap_format)
    worksheet.write_row(
        "B4:E4",
        [
            "Adresse",
            "Ville",
            "Code postal",
            "Pays",
        ],
        cell_format=wrap_format,
    )
    worksheet.merge_range("F3:F4", "Numéro d'enregistrement")
    worksheet.merge_range("G3:G4", "Date de validité de la décision de reconnaissance")
    worksheet.merge_range("H3:H4", "Biocarburants reconnus")

    # content
    row = 5
    for a in active_agreements:
        worksheet.write(row, 0, a["production_site"]["name"] if a["production_site"] else "SITE DE PROD MANQUANT")
        worksheet.write(row, 5, a["certificate_id"])

        if a["production_site"]:
            worksheet.write(row, 1, a["production_site"]["address"])
            worksheet.write(row, 2, a["production_site"]["city"])
            worksheet.write(row, 3, a["production_site"]["postal_code"])
            worksheet.write(row, 4, a["production_site"]["country"])
            worksheet.write(row, 6, a["valid_from"][:4] + "-" + a["valid_until"][:4])

            worksheet.write(row, 7, a["biofuel_list"])

        row += 1

    workbook.close()
    return location
