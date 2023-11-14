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
from doublecount.models import DoubleCountingApplication, DoubleCountingProduction
from doublecount.serializers import BiofuelSerializer, EntitySerializer, FeedStockSerializer
from producers.models import ProductionSite, ProductionSiteOutput
from django.db.models.aggregates import Count, Sum


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def get_agreements(request, *args, **kwargs):
    entity_id = int(kwargs["context"]["entity_id"])

    return JsonResponse({"status": "success", "data": []})
