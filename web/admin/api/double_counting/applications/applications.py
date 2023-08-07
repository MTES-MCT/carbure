from django.db.models.query_utils import Q

from django.http import JsonResponse
from core.decorators import is_admin_or_external_admin

from doublecount.models import (
    DoubleCountingApplication,
)
from doublecount.serializers import DoubleCountingApplicationFullSerializer


@is_admin_or_external_admin
def get_applications_admin(request):
    applications = DoubleCountingApplication.objects.filter(~Q(status__in=[DoubleCountingApplication.ACCEPTED]))

    rejected_data = applications.filter(status=DoubleCountingApplication.REJECTED)

    pending_data = applications.filter(
        ~Q(status__in=[DoubleCountingApplication.ACCEPTED, DoubleCountingApplication.REJECTED])
    )
    rejected = DoubleCountingApplicationFullSerializer(rejected_data, many=True)
    pending = DoubleCountingApplicationFullSerializer(pending_data, many=True)

    data = {
        "rejected": rejected.data,
        "pending": pending.data,
    }
    return JsonResponse({"status": "success", "data": data})
