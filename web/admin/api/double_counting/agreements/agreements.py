from django.db.models.query_utils import Q

from datetime import datetime


from django.http import JsonResponse
from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationSerializer
from core.decorators import check_admin_rights


@check_admin_rights()
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
