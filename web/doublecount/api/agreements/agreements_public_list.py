from datetime import datetime

from django.db.models.query_utils import Q
from django.http.response import JsonResponse

from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationPublicSerializer


def get_agreements_public_list(request, *args, **kwargs):
    year = datetime.now().year

    agreements_active = (
        DoubleCountingRegistration.objects.filter(Q(valid_from__year__lte=year) & Q(valid_until__year__gte=year))
        .select_related("production_site")
        .order_by("production_site__name")
    )

    active_agreements = DoubleCountingRegistrationPublicSerializer(agreements_active, many=True).data

    return JsonResponse({"status": "success", "data": active_agreements})
