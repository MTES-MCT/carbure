from typing import List
from django import forms
from django.db.models.query_utils import Q
from datetime import datetime
from django.http.response import HttpResponse, JsonResponse
import pandas as pd
import xlsxwriter

from django.http import JsonResponse
from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationSerializer
from core.common import ErrorResponse
from core.decorators import check_admin_rights
from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere
from doublecount.models import DoubleCountingApplication, DoubleCountingProduction
from doublecount.serializers import BiofuelSerializer, FeedStockSerializer
from producers.models import ProductionSite, ProductionSiteOutput
from django.db.models.aggregates import Count, Sum


class AgreementError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


@check_admin_rights()
def get_agreements(request, *args, **kwargs):
    sort_form = AgreementSortForm(request.GET)
    as_excel_file = request.GET.get("as_excel_file") == "true"

    if not sort_form.is_valid():
        return ErrorResponse(400, AgreementError.MALFORMED_PARAMS, {**sort_form.errors})

    order_by = sort_form.cleaned_data["order_by"]
    direction = sort_form.cleaned_data["direction"]

    current_year = datetime.now().year

    agreements_active = (
        DoubleCountingRegistration.objects.filter(
            Q(valid_from__year__lte=current_year) & Q(valid_until__year__gte=current_year)
        )
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
        agreements_incoming = DoubleCountingRegistration.objects.filter(Q(valid_from__year__gt=current_year)).select_related(
            "production_site"
        )
        agreements_expired = DoubleCountingRegistration.objects.filter(Q(valid_until__year__lt=current_year)).select_related(
            "production_site"
        )

        # get_quotas(current_year)
        data = {
            "active": DoubleCountingRegistrationSerializer(agreements_active, many=True).data,
            "incoming": DoubleCountingRegistrationSerializer(agreements_incoming, many=True).data,
            "expired": DoubleCountingRegistrationSerializer(agreements_expired, many=True).data,
        }
        return JsonResponse({"status": "success", "data": data})


class AgreementSortForm(forms.Form):
    order_by = forms.CharField(required=False)
    direction = forms.CharField(required=False)


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
    for a in agreements:
        worksheet.write(row, 0, a.production_site.name if a.production_site else "SITE DE PROD MANQUANT")
        worksheet.write(row, 5, a.certificate_id)

        if a.production_site:
            worksheet.write(row, 1, a.production_site.address)
            worksheet.write(row, 2, a.production_site.city)
            worksheet.write(row, 3, a.production_site.postal_code)
            worksheet.write(row, 4, a.production_site.country.name)
            worksheet.write(row, 6, a.valid_from.strftime("%Y-%m-%d") + "-" + a.valid_until.strftime("%Y-%m-%d"))

            if not a.application:
                biofuel_list = "NC"
            else:
                productions = DoubleCountingProduction.objects.filter(
                    dca=a.application, approved_quota__gt=0, year=a.valid_from.year
                )
                biofuel_list = ", ".join(
                    [production.biofuel.name + " (" + production.feedstock.name + ")" for production in productions]
                )

            worksheet.write(row, 7, biofuel_list)

        row += 1

    workbook.close()
    return location


# def get_quotas(year: int):
#     producers = {p.id: p for p in Entity.objects.filter(entity_type=Entity.PRODUCER)}
#     production_sites = {p.id: p for p in ProductionSite.objects.all()}
#     biofuels = {p.id: p for p in Biocarburant.objects.all()}
#     feedstocks = {m.id: m for m in MatierePremiere.objects.filter(is_double_compte=True)}

#     # tous les couples BC / MP pour sur une année
#     detailed_quotas = DoubleCountingProduction.objects.values(
#         "year", "dca__producer", "dca__production_site", "biofuel", "feedstock", "approved_quota"
#     ).filter(year=year, feedstock_id__in=feedstocks.keys())

#     # tous les lots pour des MP double compté groupé par couple et par année
#     production_lots = (
#         CarbureLot.objects.filter(
#             lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
#             carbure_producer__in=producers.keys(),
#             carbure_production_site__in=production_sites.keys(),
#             year=year,
#             feedstock_id__in=feedstocks.keys(),
#             biofuel_id__in=biofuels.keys(),
#         )
#         .values("year", "carbure_producer", "carbure_production_site", "feedstock", "biofuel")
#         .annotate(production_kg=Sum("weight"), lot_count=Count("id"))
#     )

#     # crée un dataframe pour les quotas par couple et par année
#     quotas_df = pd.DataFrame(detailed_quotas).rename(
#         columns={
#             "biofuel": "biofuel_id",
#             "feedstock": "feedstock_id",
#             "dca__producer": "producer_id",
#             "dca__production_site": "production_site_id",
#         }
#     )

#     # crée un dataframe pour le résumé des lots par couple et par année
#     production_lots_df = pd.DataFrame(production_lots).rename(
#         columns={
#             "carbure_producer": "producer_id",
#             "carbure_production_site": "production_site_id",
#             "feedstock": "feedstock_id",
#             "biofuel": "biofuel_id",
#         }
#     )

#     # merge les deux dataframes
#     if len(production_lots_df) == 0:
#         quotas_df["lot_count"] = 0
#         quotas_df["production_tonnes"] = 0
#         quotas_df["quotas_progression"] = 0
#         quotas_df["production_site"] = None
#         quotas_df["producer"] = None
#     else:
#         quotas_df.set_index(["biofuel_id", "feedstock_id", "year", "producer_id", "production_site_id"], inplace=True)
#         production_lots_df.set_index(
#             ["biofuel_id", "feedstock_id", "year", "producer_id", "production_site_id"],
#             inplace=True,
#         )
#         quotas_df = (
#             quotas_df.merge(production_lots_df, how="outer", left_index=True, right_index=True).fillna(0).reset_index()
#         )
#         quotas_df = quotas_df.loc[quotas_df["approved_quota"] > 0]
#         quotas_df["production_tonnes"] = round(quotas_df["production_kg"] / 1000)
#         quotas_df["quotas_progression"] = round((quotas_df["production_tonnes"] / quotas_df["approved_quota"]) * 100, 2)

#     quotas_df["feedstock"] = quotas_df["feedstock_id"].apply(lambda id: FeedStockSerializer(feedstocks[id]).data)
#     quotas_df["biofuel"] = quotas_df["biofuel_id"].apply(lambda id: BiofuelSerializer(biofuels[id]).data)
#     quotas_df["production_site"] = quotas_df["production_site_id"].apply(
#         lambda id: ProductionSite(production_sites[id]).data
#     )
#     quotas_df["producer"] = quotas_df["producere_id"].apply(lambda id: Entity(production_sites[id]).data)

#     del quotas_df["producer_id"]
#     del quotas_df["production_site_id"]
#     del quotas_df["feedstock_id"]
#     del quotas_df["biofuel_id"]
#     return quotas_df.to_dict("records")
