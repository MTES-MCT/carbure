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
from core.decorators import check_rights, is_admin, is_admin_or_external_admin
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
from doublecount.helpers import load_dc_sourcing_data as new_load_dc_sourcing, load_dc_production_data as new_load_dc_prod
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

from core.common import ErrorResponse
from doublecount.dc_sanity_checks import check_dc_globally
from doublecount.dc_parser import parse_dc_excel
from doublecount.old_helpers import load_dc_file, load_dc_sourcing_data, load_dc_production_data


@is_admin_or_external_admin
def get_agreements_admin(request):
    year = request.GET.get("year", False)
    if not year:
        return JsonResponse({"status": "error", "message": "Missing year"}, status=400)

    agreements = DoubleCountingAgreement.objects.filter(Q(period_start__year=year) | Q(period_end__year=year))
    accepted = agreements.filter(status=DoubleCountingAgreement.ACCEPTED)
    accepted_count = accepted.count()
    rejected = agreements.filter(status=DoubleCountingAgreement.REJECTED)
    rejected_count = rejected.count()
    expired = agreements.filter(status=DoubleCountingAgreement.LAPSED)
    expired_count = expired.count()
    pending = agreements.filter(status=DoubleCountingAgreement.PENDING)
    pending_count = pending.count()
    progress = agreements.filter(status=DoubleCountingAgreement.INPROGRESS)
    progress_count = progress.count()

    accepted_s = DoubleCountingAgreementFullSerializer(accepted, many=True)
    rejected_s = DoubleCountingAgreementFullSerializer(rejected, many=True)
    expired_s = DoubleCountingAgreementFullSerializer(expired, many=True)
    pending_s = DoubleCountingAgreementFullSerializer(pending, many=True)
    progress_s = DoubleCountingAgreementFullSerializer(progress, many=True)
    data = {
        "accepted": {"count": accepted_count, "agreements": accepted_s.data},
        "rejected": {"count": rejected_count, "agreements": rejected_s.data},
        "expired": {"count": expired_count, "agreements": expired_s.data},
        "progress": {"count": progress_count, "agreements": progress_s.data},
        "pending": {"count": pending_count, "agreements": pending_s.data},
    }
    return JsonResponse({"status": "success", "data": data})
