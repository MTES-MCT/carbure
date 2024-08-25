import datetime
import os
import re
import traceback
import unicodedata
from typing import List

import pandas as pd
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models.aggregates import Count, Sum
from django.http import JsonResponse

from certificates.models import DoubleCountingRegistration
from core.common import CarbureException
from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere, Pays, UserRights
from doublecount.dc_sanity_checks import (
    DoubleCountingError,
    check_dc_globally,
    check_production_row,
    check_production_row_integrity,
    check_sourcing_row,
    error,
)
from doublecount.errors import DoubleCountingError, error
from doublecount.models import DoubleCountingApplication, DoubleCountingProduction, DoubleCountingSourcing
from doublecount.parser.dc_parser import (
    ProductionForecastRow,
    ProductionMaxRow,
    RequestedQuotaRow,
    SourcingRow,
    parse_dc_excel,
)
from doublecount.serializers import (
    BiofuelSerializer,
    DoubleCountingProductionSerializer,
    DoubleCountingSourcingSerializer,
    FeedStockSerializer,
)
from producers.models import ProductionSite

today = datetime.date.today()


def send_dca_confirmation_email(dca):
    text_message = """
    Bonjour,

    Nous vous confirmons la réception de votre dossier de demande d'agrément au double-comptage.

    Bonne journée,
    L'équipe CarbuRe
    """
    email_subject = "Carbure - Dossier Double Comptage"
    cc = None
    if os.getenv("IMAGE_TAG", "dev") != "prod":
        # send only to staff / superuser
        recipients = ["carbure@beta.gouv.fr"]
    else:
        # PROD
        recipients = [
            r.user.email
            for r in UserRights.objects.filter(entity=dca.producer, user__is_staff=False, user__is_superuser=False).exclude(
                role__in=[UserRights.AUDITOR, UserRights.RO]
            )
        ]
        cc = "carbure@beta.gouv.fr"

    email = EmailMessage(
        subject=email_subject, body=text_message, from_email=settings.DEFAULT_FROM_EMAIL, to=recipients, cc=cc
    )
    email.send(fail_silently=False)


def load_dc_sourcing_data(dca: DoubleCountingApplication, sourcing_rows: List[SourcingRow]):
    # prepare error list
    sourcing_data = []
    sourcing_errors = []

    # preload data
    feedstocks = MatierePremiere.objects.all()
    countries = Pays.objects.all()

    for row in sourcing_rows:
        line = row["line"]
        meta = {"year": row["year"]}
        metric_tonnes = row["metric_tonnes"]

        if not metric_tonnes:
            continue

        errors = check_sourcing_row(row)
        if len(errors) > 0:
            sourcing_errors += errors
            continue

        # CREATE SOURCING
        sourcing = DoubleCountingSourcing(dca=dca)
        sourcing.year = row["year"]
        sourcing.metric_tonnes = row["metric_tonnes"]

        # Feedstock
        try:
            feedstock = feedstocks.get(code=row["feedstock"].strip()) if row["feedstock"] else None
        except Exception:
            feedstock = None

        if feedstock and not feedstock.is_double_compte:
            continue
        if feedstock:
            sourcing.feedstock = feedstock

        # Origin country
        origin_country = get_country(row["origin_country"], countries)
        if origin_country:
            sourcing.origin_country = origin_country
        else:
            errors.append(
                error(
                    DoubleCountingError.UNKNOWN_COUNTRY_OF_ORIGIN,
                    line=line,
                    meta=meta,
                )
            )

        sourcing.supply_country = get_country(row["supply_country"], countries)
        sourcing.transit_country = get_country(row["transit_country"], countries)

        sourcing_errors += errors
        if len(errors) == 0:
            sourcing_data.append(sourcing)

    return sourcing_data, sourcing_errors


def get_country(string, countries):
    if not string:
        return None

    country_string = string.strip()
    try:
        country = countries.get(code_pays=country_string)
    except Exception:
        country = None
        try:
            country = countries.get(name=country_string)
        except Exception:
            country = None

    return country


def load_dc_production_data(
    dca: DoubleCountingApplication,
    production_max_rows: List[ProductionMaxRow],
    production_forecast_rows: List[ProductionForecastRow],
    requested_quota_rows: List[RequestedQuotaRow],
):
    production_data = []
    production_errors = []

    # preload data
    feedstocks = MatierePremiere.objects.all()
    biofuels = Biocarburant.objects.all()

    # check rows integrity
    for index, production_base_rows in enumerate([production_max_rows, production_forecast_rows, requested_quota_rows]):
        tab_name = ["Capacité maximale de production", "Production prévisionelle", "Reconnaissance double comptage"][index]

        if len(production_base_rows) < 2:
            production_errors.append(
                error(
                    DoubleCountingError.MISSING_DATA,
                    meta={"tab_name": tab_name},
                )
            )
            continue

        for req_quota_row in production_base_rows:
            feedstock = get_material(req_quota_row["feedstock"], feedstocks)
            biofuel = get_material(req_quota_row["biofuel"], biofuels)
            errors = check_production_row_integrity(feedstock, biofuel, req_quota_row, tab_name, dca)
            production_errors += errors

    if len(production_errors) > 0:
        return production_data, production_errors

    # merge rows

    requested_quota_rows = merge_rows(requested_quota_rows, "requested_quota")
    production_forecast_rows = merge_rows(production_forecast_rows, "estimated_production")
    production_max_rows = merge_rows(production_max_rows, "max_production_capacity")

    # check data consistency from requested_quota
    for req_quota_row in requested_quota_rows:
        year = req_quota_row["year"]
        feedstock_code = req_quota_row["feedstock"]
        biofuel_code = req_quota_row["biofuel"]
        requested_quota = req_quota_row["requested_quota"]

        production = DoubleCountingProduction(dca=dca)
        production.year = year
        production.feedstock = get_material(feedstock_code, feedstocks)

        # check if feedstock is double compting
        if not production.feedstock.is_double_compte:
            production_errors.append(
                error(
                    DoubleCountingError.FEEDSTOCK_NOT_DOUBLE_COUNTING,
                    line=req_quota_row["line"],
                    meta={
                        "year": year,
                        "feedstock": feedstock_code,
                        "biofuel": biofuel_code,
                        "tab_name": "Reconnaissance double comptage",
                    },
                )
            )

        production.biofuel = get_material(biofuel_code, biofuels)
        production.requested_quota = requested_quota

        # set estimated_production
        for prod_forecast_row in production_forecast_rows:
            if (
                prod_forecast_row["year"] == year
                and prod_forecast_row["feedstock"] == feedstock_code
                and prod_forecast_row["biofuel"] == biofuel_code
            ):
                production.estimated_production = prod_forecast_row["estimated_production"]
                break

        if not production.estimated_production:
            production_errors.append(
                error(
                    DoubleCountingError.MISSING_ESTIMATED_PRODUCTION,
                    line=req_quota_row["line"],
                    meta={
                        "year": year,
                        "feedstock": feedstock_code,
                        "biofuel": biofuel_code,
                        "tab_name": "Reconnaissance double comptage",
                    },
                )
            )

        # check in production_max_rows if there is a corresponding row
        # set max_production_capacity
        for prod_max_row in production_max_rows:
            if (
                prod_max_row["year"] == req_quota_row["year"]
                and prod_max_row["feedstock"] == req_quota_row["feedstock"]
                and prod_max_row["biofuel"] == req_quota_row["biofuel"]
            ):
                production.max_production_capacity = prod_max_row["max_production_capacity"]
                break

        if not production.max_production_capacity:
            production_errors.append(
                error(
                    DoubleCountingError.MISSING_MAX_PRODUCTION_CAPACITY,
                    line=req_quota_row["line"],
                    meta={
                        "year": year,
                        "feedstock": feedstock_code,
                        "biofuel": biofuel_code,
                        "tab_name": tab_name,
                    },
                )
            )

        if len(production_errors) > 0:
            continue

        production_errors += check_production_row(production, req_quota_row)
        if len(production_errors) == 0:
            production_data.append(production)

    return production_data, production_errors


def get_material(code, list):
    try:
        return list.get(code=code)
    except Exception:
        return None


def merge_rows(rows, key_to_merge):
    merged_data = {}
    for row in rows:
        key = (row["year"], row["biofuel"], row["feedstock"])
        if key in merged_data:
            merged_data[key][key_to_merge] += row[key_to_merge]
        else:
            merged_data[key] = row
    return list(merged_data.values())


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


def load_dc_period(start_year):
    errors = []
    # if start_year == 0:
    #     errors.append(
    #         error(
    #             DoubleCountingError.MISSING_PERIOD,
    #         )
    #     )

    end_year = start_year + 1
    start = datetime.date(end_year - 1, 1, 1)
    end = datetime.date(end_year, 12, 31)
    return start, end, errors


@transaction.atomic
def check_dc_file(file):
    try:
        filepath = load_dc_filepath(file)
        (
            info,
            sourcing_forecast_rows,
            production_max_rows,
            production_forecast_rows,
            requested_quota_rows,
        ) = parse_dc_excel(filepath)
        start, end, global_errors = load_dc_period(info["start_year"])

        # create temporary agreement to hold all the data that will be parsed
        dca = DoubleCountingApplication(
            period_start=start,
            period_end=end,
        )

        sourcing_forecast_data, sourcing_forecast_errors = load_dc_sourcing_data(dca, sourcing_forecast_rows)

        production_data, production_errors = load_dc_production_data(
            dca, production_max_rows, production_forecast_rows, requested_quota_rows
        )

        global_errors += check_dc_globally(sourcing_forecast_data, production_data) if len(production_errors) == 0 else []

        return (
            info,
            {
                "sourcing_forecast": sourcing_forecast_errors,
                "production": production_errors,
                "global": global_errors,
            },
            DoubleCountingSourcingSerializer(sourcing_forecast_data, many=True).data,
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

    info = {"production_site": None, "start_year": 0, "producer_email": None}
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
    if not feedstock or not production_site:
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
        except Exception:
            dc_certificate = production_site.dc_reference
    else:
        dc_certificate = None
    return dc_certificate


def send_dca_status_email(dca):
    if dca.status == DoubleCountingApplication.ACCEPTED:
        text_message = """
        Bonjour,

        Votre dossier de demande d'agrément au double-comptage pour le site de production %s a été accepté.

        Bonne journée,
        L'équipe CarbuRe
        """ % (dca.production_site.name)
    elif dca.status == DoubleCountingApplication.REJECTED:
        text_message = """
        Bonjour,

        Votre dossier de demande d'agrément au double-comptage pour le site de production %s a été rejeté.

        Bonne journée,
        L'équipe CarbuRe
        """ % (dca.production_site.name)
    else:
        # no mail to send
        return
    email_subject = "Carbure - Dossier Double Comptage"
    cc = None
    if os.getenv("IMAGE_TAG", "dev") != "prod":
        # send only to staff / superuser
        recipients = ["carbure@beta.gouv.fr"]
    else:
        # PROD
        recipients = [
            r.user.email
            for r in UserRights.objects.filter(entity=dca.producer, user__is_staff=False, user__is_superuser=False).exclude(
                role__in=[UserRights.AUDITOR, UserRights.RO]
            )
        ]
        cc = "carbure@beta.gouv.fr"
    email = EmailMessage(
        subject=email_subject, body=text_message, from_email=settings.DEFAULT_FROM_EMAIL, to=recipients, cc=cc
    )
    email.send(fail_silently=False)


def get_quotas(year: int, producer_id: int = None):
    producers_query = Entity.objects.filter(entity_type=Entity.PRODUCER)
    if producer_id is not None:
        producers_query = producers_query.filter(id=producer_id)
    producers = {p.id: p for p in producers_query}
    production_sites = {p.id: p for p in ProductionSite.objects.all()}
    biofuels = {p.id: p for p in Biocarburant.objects.all()}
    feedstocks = {m.id: m for m in MatierePremiere.objects.filter(is_double_compte=True)}

    # tous les couples BC / MP pour sur une année
    detailed_quotas = DoubleCountingProduction.objects.values(
        "year", "dca__producer", "dca__production_site", "biofuel", "feedstock", "approved_quota", "dca__certificate_id"
    ).filter(year=year, feedstock_id__in=feedstocks.keys(), approved_quota__gt=0)

    # tous les lots pour des MP double compté groupé par couple et par année
    production_lots = (
        CarbureLot.objects.filter(
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
            delivery_type__in=[CarbureLot.DIRECT, CarbureLot.RFC, CarbureLot.BLENDING],
            carbure_producer__in=producers.keys(),
            carbure_production_site__in=production_sites.keys(),
            year=year,
            feedstock_id__in=feedstocks.keys(),
            biofuel_id__in=biofuels.keys(),
        )
        .values("year", "carbure_producer", "carbure_production_site", "feedstock", "biofuel")
        .annotate(production_kg=Sum("weight"), lot_count=Count("id"))
    )

    # crée un dataframe pour les quotas par couple et par année
    quotas_df = pd.DataFrame(detailed_quotas).rename(
        columns={
            "biofuel": "biofuel_id",
            "feedstock": "feedstock_id",
            "dca__producer": "producer_id",
            "dca__production_site": "production_site_id",
            "dca__certificate_id": "certificate_id",
        }
    )

    # crée un dataframe pour le résumé des lots par couple et par année
    production_lots_df = pd.DataFrame(production_lots).rename(
        columns={
            "carbure_producer": "producer_id",
            "carbure_production_site": "production_site_id",
            "feedstock": "feedstock_id",
            "biofuel": "biofuel_id",
        }
    )

    # merge les deux dataframes
    if len(production_lots_df) == 0:
        grouped = []
        quotas_df["quotas_progression"] = 0
    else:
        quotas_df.set_index(["biofuel_id", "feedstock_id", "year", "producer_id", "production_site_id"], inplace=True)
        production_lots_df.set_index(
            ["biofuel_id", "feedstock_id", "year", "producer_id", "production_site_id"],
            inplace=True,
        )
        quotas_df = (
            quotas_df.merge(production_lots_df, how="outer", left_index=True, right_index=True).fillna(0).reset_index()
        )
        quotas_df = quotas_df.loc[quotas_df["approved_quota"] > 0]
        quotas_df["production_tonnes"] = round(quotas_df["production_kg"] / 1000)
        quotas_df["quotas_progression"] = round((quotas_df["production_tonnes"] / quotas_df["approved_quota"]), 2)

        grouped = quotas_df.groupby(["year", "producer_id", "production_site_id", "certificate_id"]).agg(
            quotas_progression=("quotas_progression", "mean"),
        )
        grouped.reset_index(inplace=True)

    return grouped.to_dict("records") if len(grouped) > 0 else []


def get_agreement_quotas(agreement: DoubleCountingRegistration):
    application = agreement.application
    if not application or application.status != DoubleCountingApplication.ACCEPTED:
        return None

    biofuels = {p.id: p for p in Biocarburant.objects.all()}
    feedstocks = {m.id: m for m in MatierePremiere.objects.filter(is_double_compte=True)}

    # tous les couples BC / MP pour le site de production sur une année
    detailed_quotas = DoubleCountingProduction.objects.values("biofuel", "feedstock", "approved_quota", "year").filter(
        dca_id=application.id, approved_quota__gt=0
    )

    # tous les lots pour des MP double compté pour le site de production regroupé par couple et par année
    production_lots = (
        CarbureLot.objects.filter(
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
            delivery_type__in=[CarbureLot.DIRECT, CarbureLot.RFC, CarbureLot.BLENDING],
            carbure_production_site_id=application.production_site,
        )
        .values("year", "feedstock", "biofuel")
        .filter(feedstock_id__in=feedstocks.keys(), year__in=[agreement.valid_from.year, agreement.valid_from.year + 1])
        .annotate(production_kg=Sum("weight"), lot_count=Count("id"))
    )

    # crée un dataframe pour les quotas par couple et par année
    quotas_df = pd.DataFrame(detailed_quotas).rename(columns={"biofuel": "biofuel_id", "feedstock": "feedstock_id"})

    # crée un dataframe pour le résumé des lots par couple et par année
    production_lots_df = pd.DataFrame(production_lots).rename(columns={"feedstock": "feedstock_id", "biofuel": "biofuel_id"})

    # merge les deux dataframes

    if len(production_lots_df) == 0:
        quotas_df["lot_count"] = 0
        quotas_df["production_tonnes"] = 0
        quotas_df["quotas_progression"] = 0
    else:
        quotas_df.set_index(["biofuel_id", "feedstock_id", "year"], inplace=True)
        production_lots_df.set_index(["biofuel_id", "feedstock_id", "year"], inplace=True)
        quotas_df = (
            quotas_df.merge(production_lots_df, how="outer", left_index=True, right_index=True).fillna(0).reset_index()
        )
        quotas_df = quotas_df.loc[quotas_df["approved_quota"] > 0]
        quotas_df["production_tonnes"] = round(quotas_df["production_kg"] / 1000)
        quotas_df["quotas_progression"] = round((quotas_df["production_tonnes"] / quotas_df["approved_quota"]), 2)

    quotas_df["feedstock"] = quotas_df["feedstock_id"].apply(lambda id: FeedStockSerializer(feedstocks[id]).data)
    quotas_df["biofuel"] = quotas_df["biofuel_id"].apply(lambda id: BiofuelSerializer(biofuels[id]).data)

    del quotas_df["feedstock_id"]
    del quotas_df["biofuel_id"]
    return quotas_df.to_dict("records")
