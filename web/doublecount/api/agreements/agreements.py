from datetime import datetime

from django.http import JsonResponse
from django.http.response import JsonResponse

from certificates.models import DoubleCountingRegistration
from core.decorators import check_user_rights
from core.models import UserRights
from doublecount.helpers import get_quotas
from doublecount.models import DoubleCountingApplication
from doublecount.serializers import (
    DoubleCountingApplicationPartialSerializer,
)


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def get_agreements(request, *args, **kwargs):
    entity_id = int(kwargs["context"]["entity_id"])

    applications = DoubleCountingApplication.objects.filter(producer_id=entity_id)
    if len(applications) == 0:
        return JsonResponse({"status": "success", "data": []})

    applications_data = DoubleCountingApplicationPartialSerializer(applications, many=True).data
    print(">>>applications_data: ", applications_data)
    current_year = datetime.now().year

    quotas = get_quotas(year=current_year, producer_id=entity_id)

    # add quotas to active agreements
    for application in applications_data:
        if application["status"] != DoubleCountingApplication.ACCEPTED:
            application["quotas_progression"] = None
            continue
        found_quotas = [q for q in quotas if q["certificate_id"] == application["certificate_id"]]
        application["quotas_progression"] = round(found_quotas[0]["quotas_progression"], 2) if len(found_quotas) > 0 else 0

        # add agreement_id to applications when accepted
        try:
            agreement = DoubleCountingRegistration.objects.get(application_id=application["id"])
            application["agreement_id"] = agreement.id
        except Exception:
            application["agreement_id"] = None

    return JsonResponse({"status": "success", "data": applications_data})


def add_quotas_to_applications(year: int, agreements):
    return agreements
