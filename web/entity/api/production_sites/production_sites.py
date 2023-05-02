import datetime
import traceback
from dateutil.relativedelta import *

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Q
from django_otp.decorators import otp_required
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from api.v4.helpers import get_prefetched_data
from core.carburetypes import CarbureSanityCheckErrors

from core.models import (
    CarbureLot,
    CarbureLotReliabilityScore,
    CarbureStock,
    Entity,
    GenericError,
    UserRights,
    Pays,
    MatierePremiere,
    Biocarburant,
    Depot,
    EntityDepot,
)
from core.serializers import EntityCertificateSerializer, GenericCertificateSerializer
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput
from core.decorators import check_rights, otp_or_403

from certificates.models import ProductionSiteCertificate

from core.models import UserRightsRequests, UserRights
from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring


@check_rights("entity_id")
def get_production_sites(request, *args, **kwargs):
    context = kwargs["context"]
    psites = ProductionSite.objects.filter(producer=context["entity"])

    psitesbyid = {p.id: p for p in psites}
    for k, v in psitesbyid.items():
        v.inputs = []
        v.outputs = []

    data = []

    for ps in psites:
        psite_data = ps.natural_key()
        psite_data["inputs"] = [i.natural_key() for i in ps.productionsiteinput_set.all()]
        psite_data["outputs"] = [o.natural_key() for o in ps.productionsiteoutput_set.all()]
        psite_data["certificates"] = GenericCertificateSerializer(
            [p.certificate.certificate for p in ps.productionsitecertificate_set.all()], many=True
        ).data
        data.append(psite_data)

    return JsonResponse({"status": "success", "data": data})
