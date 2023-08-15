import datetime
from django.core.mail import EmailMessage
import os
from typing import List
from django.http import JsonResponse
from django.conf import settings
import traceback
import unicodedata
import re
from django.db import transaction
from certificates.models import DoubleCountingRegistration
from core.models import Pays, Biocarburant, MatierePremiere, UserRights
from doublecount.models import DoubleCountingSourcing, DoubleCountingProduction
from doublecount.dc_sanity_checks import check_production_row, check_production_row_integrity, check_sourcing_row
from doublecount.models import DoubleCountingApplication
from doublecount.parser.dc_parser import (
    ProductionForecastRow,
    ProductionMaxRow,
    RequestedQuotaRow,
    SourcingRow,
    parse_dc_excel,
)
from doublecount.errors import DoubleCountingError, error


from core.common import CarbureException
from doublecount.dc_sanity_checks import check_dc_globally, error, DoubleCountingError
from doublecount.serializers import DoubleCountingProductionSerializer, DoubleCountingSourcingSerializer

today = datetime.date.today()


def load_dc_sourcing_data(dca: DoubleCountingApplication, sourcing_rows: List[SourcingRow]):
    # prepare error list
    sourcing_data = []
    sourcing_errors = []

    # preload data
    feedstocks = MatierePremiere.objects.all()
    countries = Pays.objects.all()

    for row in sourcing_rows:
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
    dca: DoubleCountingApplication,
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
            feedstock = feedstocks.get(req_quota_row["feedstock"], None)
            biofuel = biofuels.get(req_quota_row["biofuel"], None)
            errors = check_production_row_integrity(feedstock, biofuel, req_quota_row, tab_name, dca)
            production_errors += errors

    if len(production_errors) > 0:
        return production_data, production_errors

    # check data consistency from requested_quota
    for req_quota_row in requested_quota_rows:
        production = DoubleCountingProduction(dca=dca)
        for prod_forecast_row in production_forecast_rows:
            if (
                prod_forecast_row["year"] == req_quota_row["year"]
                and prod_forecast_row["feedstock"] == req_quota_row["feedstock"]
                and prod_forecast_row["biofuel"] == req_quota_row["biofuel"]
            ):
                production.estimated_production = prod_forecast_row["estimated_production"]
                break

        if not production.estimated_production:
            production_errors.append(
                error(
                    DoubleCountingError.MISSING_ESTIMATED_PRODUCTION,
                    line=req_quota_row["line"],
                    meta={
                        "year": req_quota_row["year"],
                        "feedstock": req_quota_row["feedstock"],
                        "biofuel": req_quota_row["biofuel"],
                        "tab_name": "Reconnaissance double comptage",
                    },
                )
            )

        # check in production_max_rows if there is a corresponding row
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
                        "year": req_quota_row["year"],
                        "feedstock": req_quota_row["feedstock"],
                        "biofuel": req_quota_row["biofuel"],
                        "tab_name": tab_name,
                    },
                )
            )

        production.year = req_quota_row["year"]
        production.feedstock = feedstocks.get(req_quota_row["feedstock"], None)
        production.biofuel = biofuels.get(req_quota_row["biofuel"], None)
        production.requested_quota = req_quota_row["requested_quota"]

        if len(production_errors) > 0:
            return production_data, production_errors

        production_errors += check_production_row(production, req_quota_row)
        production_data.append(production)

    return production_data, production_errors


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
            tracability,
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
        except:
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
        """ % (
            dca.production_site.name
        )
    elif dca.status == DoubleCountingApplication.REJECTED:
        text_message = """
        Bonjour,

        Votre dossier de demande d'agrément au double-comptage pour le site de production %s a été accepté.

        Bonne journée,
        L'équipe CarbuRe
        """ % (
            dca.production_site.name
        )
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
