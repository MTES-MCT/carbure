import datetime
from typing import List
from django.http import JsonResponse
import traceback
import unicodedata
import re
from django.db import transaction
from requests import Request
from certificates.models import DoubleCountingRegistration
from core.models import Pays, Biocarburant, MatierePremiere
from doublecount.models import DoubleCountingSourcing, DoubleCountingProduction
from doublecount.dc_sanity_checks import check_production_row, check_production_row_integrity, check_sourcing_row
from doublecount.models import DoubleCountingAgreement
from doublecount.dc_parser import (
    ProductionBaseRow,
    ProductionForecastRow,
    ProductionMaxRow,
    RequestedQuotaRow,
    SourcingRow,
    ProductionRow,
)
from doublecount.errors import DoubleCountingError, error


from core.common import CarbureException
from doublecount.dc_sanity_checks import check_dc_globally, error, DoubleCountingError
from doublecount.dc_parser import parse_dc_excel
from doublecount.serializers import DoubleCountingProductionSerializer, DoubleCountingSourcingSerializer

today = datetime.date.today()


def load_dc_sourcing_data(dca: DoubleCountingAgreement, sourcing_rows: List[SourcingRow]):
    # prepare error list
    sourcing_data = []
    sourcing_errors = []

    # preload data
    feedstocks = MatierePremiere.objects.all()
    countries = Pays.objects.all()

    for row in sourcing_rows:
        # skip rows that start empty
        if not row["year"]:
            continue

        if row["year"] == -1:
            sourcing_errors.append(error(DoubleCountingError.UNKNOWN_YEAR, line=row["line"]))
            continue

        try:
            feedstock = feedstocks.get(code=row["feedstock"].strip()) if row["feedstock"] else None
        except:
            feedstock = None

        try:
            origin_country = countries.get(code_pays=row["origin_country"].strip()) if row["origin_country"] else None
        except:
            origin_country = None

        try:
            supply_country = countries.get(code_pays=row["supply_country"].strip()) if row["supply_country"] else None
        except:
            supply_country = None

        try:
            transit_country = countries.get(code_pays=row["transit_country"].strip()) if row["transit_country"] else None
        except:
            transit_country = None

        sourcing = DoubleCountingSourcing(dca=dca)
        sourcing.year = row["year"]
        if feedstock:
            sourcing.feedstock = feedstock
        if origin_country:
            sourcing.origin_country = origin_country
        sourcing.supply_country = supply_country
        sourcing.transit_country = transit_country
        sourcing.metric_tonnes = row["metric_tonnes"]
        errors = check_sourcing_row(sourcing, row)
        sourcing_errors += errors
        if len(errors) == 0:
            sourcing_data.append(sourcing)

    return sourcing_data, sourcing_errors


def load_dc_production_data(
    dca: DoubleCountingAgreement,
    production_max_rows: List[ProductionMaxRow],
    production_forecast_rows: List[ProductionForecastRow],
    requested_quota_rows: List[RequestedQuotaRow],
):
    production_data = []
    production_errors = []

    # preload data
    feedstocks = {f.code: f for f in MatierePremiere.objects.all()}
    biofuels = {f.code: f for f in Biocarburant.objects.all()}

    # check rows integrity
    for index, production_base_row in enumerate([production_max_rows, production_forecast_rows, requested_quota_rows]):
        tabName = ["Capacité maximale de production", "Production prévisionelle", "Reconnaissance double comptage"][index]
        for row in production_base_row:
            feedstock = feedstocks.get(row["feedstock"], None)
            biofuel = biofuels.get(row["biofuel"], None)
            errors = check_production_row_integrity(feedstock, biofuel, row, tabName)
            production_errors += errors

    if len(production_errors) > 0:
        return production_data, production_errors

    # VERIFIER EN PARTANT DES REQUESTED QUOTA
    # ET DESCENDRE POUR VERIFIER LA CORRESPONDANCE AVEC L'ONGLET PRODUCTION
    # for row in requested_quota_rows:
    #     # skip rows that start empty
    #     if not row["year"]:
    #         continue

    #     feedstock = feedstocks.get(row["feedstock"], None)
    #     biofuel = biofuels.get(row["biofuel"], None)

    #     production = DoubleCountingProduction(dca=dca)
    #     production.year = row["year"]
    #     production.feedstock = feedstock
    #     production.biofuel = biofuel

    #     errors = check_production_row_integrity(production, row)
    #     production_errors += errors
    #     if len(errors) == 0:
    #         production_data.append(production)

    return production_data, production_errors


# def load_dc_production_data(dca: DoubleCountingAgreement, production_rows: List[ProductionRow]):
#     print(" ")
#     print("dca.period_start: ", dca.period_start)
#     production_data = []
#     production_errors = []

#     # preload data
#     feedstocks = {f.code: f for f in MatierePremiere.objects.all()}
#     biofuels = {f.code: f for f in Biocarburant.objects.all()}

#     for row in production_rows:
#         # skip rows that start empty
#         if not row["year"]:
#             continue

#         feedstock = feedstocks.get(row["feedstock"], None)
#         biofuel = biofuels.get(row["biofuel"], None)
#         production = DoubleCountingProduction(dca=dca)
#         production.year = row["year"]
#         production.feedstock = feedstock
#         production.biofuel = biofuel
#         production.max_production_capacity = row["max_production_capacity"]
#         production.estimated_production = row["estimated_production"]
#         production.requested_quota = row["requested_quota"]

#         errors = check_production_row(production, row)
#         production_errors += errors
#         if len(errors) == 0:
#             production_data.append(production)

#     return production_data, production_errors


def load_dc_recognition_file(entity, psite_id, user, filepath):
    return JsonResponse({"status": "error", "message": "not implemented"}, status=400)


def load_dc_filepath(file):
    directory = "/tmp"
    now = datetime.datetime.now()
    filename = "%s_%s.xlsx" % (now.strftime("%Y%m%d.%H%M%S"), file.name.upper())
    filename = "".join((c for c in unicodedata.normalize("NFD", filename) if unicodedata.category(c) != "Mn"))
    filepath = "%s/%s" % (directory, filename)

    # save file
    with open(filepath, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return filepath


def load_dc_period(info, requested_quota_rows):
    years = [production["year"] for production in requested_quota_rows]
    end_year = max(years) if len(years) > 0 else info["year"] + 1
    start = datetime.date(end_year - 1, 1, 1)
    end = datetime.date(end_year, 12, 31)
    return start, end


@transaction.atomic
def check_dc_file(file):
    try:
        filepath = load_dc_filepath(file)
        # info, sourcing_forecast_rows, production_rows = parse_dc_excel(filepath)
        info, sourcing_forecast_rows, production_max_rows, production_forecast_rows, requested_quota_rows = parse_dc_excel(
            filepath
        )
        start, end = load_dc_period(info, requested_quota_rows)
        # start, end = load_dc_period(info, production_rows)

        # create temporary agreement to hold all the data that will be parsed
        dca = DoubleCountingAgreement(
            period_start=start,
            period_end=end,
        )
        sourcing_forecast_data, sourcing_forecast_errors = load_dc_sourcing_data(dca, sourcing_forecast_rows)
        # production_data, production_errors = load_dc_production_data(dca, production_rows)
        production_data, production_errors = load_dc_production_data(
            dca, production_max_rows, production_forecast_rows, requested_quota_rows
        )

        sourcing_data = sourcing_forecast_data

        # sourcing_data = sourcing_history_data + sourcing_forecast_data
        global_errors = check_dc_globally(sourcing_data, production_data)

        return (
            info,
            {
                # "sourcing_history": sourcing_history_errors,
                "sourcing_forecast": sourcing_forecast_errors,
                "production": production_errors,
                "global": global_errors,
            },
            DoubleCountingSourcingSerializer(sourcing_data, many=True).data,
            DoubleCountingProductionSerializer(production_data, many=True).data,
        )

    except CarbureException as e:
        if e.error == DoubleCountingError.BAD_WORKSHEET_NAME:
            excel_error = error(DoubleCountingError.BAD_WORKSHEET_NAME, is_blocking=True, meta=e.meta)

    except Exception as e:
        traceback.print_exc()

        # bad tab name
        sheetNameRegexp = r"'Worksheet (.*) does not exist.'"
        matchedSheet = re.match(sheetNameRegexp, str(e))
        if matchedSheet:
            sheetName = matchedSheet[1]
            excel_error = error(
                DoubleCountingError.BAD_WORKSHEET_NAME,
                is_blocking=True,
                meta={"sheet_name": sheetName},
            )
        elif str(e) == "year 0 is out of range":
            excel_error = error(DoubleCountingError.UNKNOWN_YEAR, is_blocking=True)
        else:
            excel_error = error(DoubleCountingError.EXCEL_PARSING_ERROR, is_blocking=True, meta=str(e))

    info = {"production_site": None, "year": 0, "producer_email": None}
    return (
        info,
        {
            "sourcing_forecast": [],
            # "sourcing_history": [],
            "production": [],
            "global": [excel_error],
        },
        None,
        None,
    )


def get_lot_dc_agreement(feedstock, delivery_date, production_site):
    if not feedstock:
        return None

    dc_certificate = ""
    if feedstock and feedstock.is_double_compte and production_site.dc_reference:
        try:
            pd_certificates = DoubleCountingRegistration.objects.filter(
                production_site_id=production_site.id,
                valid_from__lt=delivery_date,
                valid_until__gte=delivery_date,
            )
            current_certificate = pd_certificates.first()
            if current_certificate:
                dc_certificate = current_certificate.certificate_id
            else:  # le certificat renseigné sur le site de production est mis par defaut
                dc_certificate = production_site.dc_reference
        except:
            dc_certificate = production_site.dc_reference
    else:
        dc_certificate = None
    return dc_certificate
