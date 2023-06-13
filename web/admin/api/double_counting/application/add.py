import datetime
from email import message
import os
import traceback
import unicodedata
import boto3
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import json
from django.db.models.aggregates import Count, Sum
from django.db.models.query_utils import Q

import xlsxwriter
from django.http import JsonResponse, HttpResponse
from core.decorators import check_admin_rights, check_rights, is_admin, is_admin_or_external_admin
import pytz
import traceback
import pandas as pd

from producers.models import ProductionSite
from doublecount.models import (
    DoubleCountingAgreement,
    DoubleCountingDocFile,
    DoubleCountingSourcing,
    DoubleCountingProduction,
)
from doublecount.serializers import DoubleCountingAgreementFullSerializer, DoubleCountingAgreementPartialSerializer
from doublecount.serializers import (
    DoubleCountingAgreementFullSerializerWithForeignKeys,
    DoubleCountingAgreementPartialSerializerWithForeignKeys,
)
from doublecount.helpers import (
    check_dc_file,
    load_dc_filepath,
    load_dc_period,
    load_dc_sourcing_data,
    load_dc_production_data,
)
from core.models import Entity, UserRights, MatierePremiere, Pays, Biocarburant, CarbureLot
from core.xlsx_v3 import (
    export_dca,
    make_biofuels_sheet,
    make_dc_mps_sheet,
    make_countries_sheet,
    make_dc_production_sheet,
    make_dc_sourcing_sheet,
)
from carbure.storage_backends import AWSStorage
from django.core.files.storage import FileSystemStorage

from core.common import ErrorResponse, SuccessResponse
from doublecount.dc_sanity_checks import check_dc_globally
from doublecount.dc_parser import parse_dc_excel

from django.db import transaction


class DoubleCountingAddError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    PRODUCER_NOT_FOUND = "PRODUCER_NOT_FOUND"
    PRODUCTION_SITE_NOT_FOUND = "PRODUCTION_SITE_NOT_FOUND"


@check_admin_rights()
@transaction.atomic
def add_application(request, *args, **kwargs):
    producer_id = request.POST.get("producer_id", None)
    production_site_id = request.POST.get("production_site_id", None)
    file = request.FILES.get("file")

    if not production_site_id:
        return ErrorResponse(400, DoubleCountingAddError.MALFORMED_PARAMS)

    try:
        producer = Entity.objects.get(id=producer_id)
    except:
        return ErrorResponse(400, DoubleCountingAddError.PRODUCER_NOT_FOUND)

    if not ProductionSite.objects.filter(producer_id=producer_id, id=production_site_id).exists():
        return ErrorResponse(400, DoubleCountingAddError.PRODUCTION_SITE_NOT_FOUND)

    if file is None:
        return ErrorResponse(400, DoubleCountingAddError.MALFORMED_PARAMS)

    # load dc Data

    filepath = load_dc_filepath(file)
    info, sourcing_forecast, production_forecast = parse_dc_excel(filepath)
    start, end = load_dc_period(info, production_forecast)

    dca, _ = DoubleCountingAgreement.objects.get_or_create(
        producer=producer,
        production_site_id=production_site_id,
        period_start=start,
        period_end=end,
        defaults={"producer_user": request.user},
    )

    # save all production_data DoubleCountingProduction in db
    sourcing_forecast_data, _ = load_dc_sourcing_data(dca, sourcing_forecast)
    production_data, _ = load_dc_production_data(dca, production_forecast)
    DoubleCountingSourcing.objects.filter(dca=dca).delete()
    for sourcing in sourcing_forecast_data:
        sourcing.save()
    DoubleCountingProduction.objects.filter(dca=dca).delete()
    for production in production_data:
        production.save()

    # try:
    #     send_dca_confirmation_email(dca)
    # except:
    #     print("email send error")
    #     traceback.print_exc()
    return SuccessResponse()
