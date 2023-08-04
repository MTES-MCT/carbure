import datetime
from email import message
from nis import cat
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
from admin.api.double_counting.applications.add import send_dca_confirmation_email
from certificates.models import DoubleCountingRegistration
from core.decorators import check_admin_rights, check_rights, is_admin, is_admin_or_external_admin
import pytz
import traceback
import pandas as pd

from producers.models import ProductionSite
from doublecount.models import (
    DoubleCountingApplication,
    DoubleCountingDocFile,
    DoubleCountingSourcing,
    DoubleCountingProduction,
)
from doublecount.serializers import DoubleCountingApplicationFullSerializer, DoubleCountingApplicationPartialSerializer
from doublecount.serializers import (
    DoubleCountingApplicationFullSerializerWithForeignKeys,
    DoubleCountingApplicationPartialSerializerWithForeignKeys,
)
from doublecount.helpers import (
    load_dc_sourcing_data as new_load_dc_sourcing,
    load_dc_production_data as new_load_dc_prod,
    send_dca_status_email,
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
from doublecount.parser.dc_parser import parse_dc_excel
from doublecount.old_helpers import load_dc_file, load_dc_sourcing_data, load_dc_production_data
from resources.factories import production_site


class DoubleCountingApplicationApproveError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"
    QUOTAS_NOT_APPROVED = "QUOTAS_NOT_APPROVED"


@check_admin_rights()
def approve_dca(request, *args, **kwargs):
    dca_id = request.POST.get("dca_id", False)
    if not dca_id:
        return ErrorResponse(400, DoubleCountingApplicationApproveError.MALFORMED_PARAMS)

    try:
        application = DoubleCountingApplication.objects.get(id=dca_id)
    except:
        return ErrorResponse(400, DoubleCountingApplicationApproveError.APPLICATION_NOT_FOUND)

    # ensure all quotas have been validated
    remaining_quotas_to_check = DoubleCountingProduction.objects.filter(dca=application, approved_quota=-1).count()
    if remaining_quotas_to_check > 0:
        return ErrorResponse(400, DoubleCountingApplicationApproveError.QUOTAS_NOT_APPROVED)

    application.status = DoubleCountingApplication.ACCEPTED
    application.save()  # save before sending email, just in case

    # create Agreement

    production_site_address = (
        application.production_site.address
        + ""
        + application.production_site.city
        + ""
        + application.production_site.postal_code
        + ""
        + application.production_site.country.name
    )
    try:
        DoubleCountingRegistration.objects.update_or_create(
            certificate_id=application.agreement_id,
            certificate_holder=application.producer.name,
            production_site=application.production_site,
            registered_address=production_site_address,
            valid_from=application.period_start,
            valid_until=application.period_end,
        )
    except:
        return ErrorResponse(400, "Error while creating Agreement")

    send_dca_status_email(application)
    return SuccessResponse()
