from django.db.models.query_utils import Q
from datetime import datetime
from django.http.response import JsonResponse

from django.http import JsonResponse
from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationSerializer


def get_agreements_public_list():

    year = datetime.now().year

    agreements_active = (
        DoubleCountingRegistration.objects.filter(Q(valid_from__year__lte=year) & Q(valid_until__year__gte=year))
        .select_related("production_site")
        .order_by("production_site__name")
    )

    active_agreements = DoubleCountingRegistrationSerializer(agreements_active, many=True).data

    data = {
        "active": active_agreements,
        # "incoming": DoubleCountingRegistrationSerializer(agreements_incoming, many=True).data,
        # "expired": DoubleCountingRegistrationSerializer(agreements_expired, many=True).data,
    }
    return JsonResponse({"status": "success", "data": data})
