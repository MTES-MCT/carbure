from django.db.models.query_utils import Q

from datetime import datetime

import os
import traceback
import unicodedata
import boto3
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models.aggregates import Count, Sum

import xlsxwriter
from django.http import JsonResponse, HttpResponse
from admin.api.double_counting.applications.add import send_dca_confirmation_email
from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationSerializer
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
from doublecount.serializers import DoubleCountingApplicationPartialSerializer
from doublecount.serializers import (
    DoubleCountingApplicationPartialSerializerWithForeignKeys,
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

from doublecount.old_helpers import load_dc_file, load_dc_sourcing_data, load_dc_production_data


# @check_admin_rights()
@is_admin_or_external_admin
def get_agreements(request, *args, **kwargs):
    current_year = datetime.now().year

    agreements_active = DoubleCountingRegistration.objects.filter(
        Q(valid_from__year__lte=current_year) & Q(valid_until__year__gte=current_year)
    ).select_related("production_site")
    agreements_incoming = DoubleCountingRegistration.objects.filter(Q(valid_from__year__gt=current_year)).select_related(
        "production_site"
    )
    agreements_expired = DoubleCountingRegistration.objects.filter(Q(valid_until__year__lt=current_year)).select_related(
        "production_site"
    )

    data = {
        "active": DoubleCountingRegistrationSerializer(agreements_active, many=True).data,
        "incoming": DoubleCountingRegistrationSerializer(agreements_incoming, many=True).data,
        "expired": DoubleCountingRegistrationSerializer(agreements_expired, many=True).data,
    }
    return JsonResponse({"status": "success", "data": data})
