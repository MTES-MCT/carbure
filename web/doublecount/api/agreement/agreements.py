from pprint import pprint
from typing import Dict, List
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
from core.decorators import check_admin_rights, check_user_rights
from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere, UserRights
from core.serializers import ProductionSiteSerializer
from doublecount.helpers import get_quotas
from doublecount.models import DoubleCountingApplication, DoubleCountingProduction
from doublecount.serializers import (
    BiofuelSerializer,
    DoubleCountingApplicationPartialSerializer,
    EntitySerializer,
    FeedStockSerializer,
)
from producers.models import ProductionSite, ProductionSiteOutput
from django.db.models.aggregates import Count, Sum


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def get_agreements(request, *args, **kwargs):
    entity_id = int(kwargs["context"]["entity_id"])

    applications = DoubleCountingApplication.objects.filter(producer_id=entity_id)
    if len(applications) == 0:
        return JsonResponse({"status": "success", "data": []})

    applications_data = DoubleCountingApplicationPartialSerializer(applications, many=True).data
    current_year = datetime.now().year

    quotas = get_quotas(year=current_year, producer_id=entity_id)

    # add quotas to active agreements
    for application in applications_data:
        if application["status"] in [DoubleCountingApplication.PENDING, DoubleCountingApplication.REJECTED]:
            application["quotas_progression"] = None
            continue
        found_quotas = [q for q in quotas if q["agreement_id"] == application["agreement_id"]]
        application["quotas_progression"] = round(found_quotas[0]["quotas_progression"], 2) if len(found_quotas) > 0 else 0

    return JsonResponse({"status": "success", "data": applications_data})


def add_quotas_to_applications(year: int, agreements):
    return agreements
