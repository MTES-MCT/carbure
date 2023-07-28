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
    # accepted = applications.filter(status=DoubleCountingApplication.ACCEPTED)
    # accepted_count = accepted.count()
    rejected_data = applications.filter(status=DoubleCountingApplication.REJECTED)
    pending_data = applications.filter(status__in=[DoubleCountingApplication.PENDING])
    inprogress_data = applications.filter(status=DoubleCountingApplication.INPROGRESS)
    # accepted_s = DoubleCountingApplicationFullSerializer(accepted, many=True)
    rejected = DoubleCountingApplicationFullSerializer(rejected_data, many=True)
    pending = DoubleCountingApplicationFullSerializer(pending_data, many=True)
    inprogress = DoubleCountingApplicationFullSerializer(inprogress_data, many=True)

    data = {
        # "accepted": {"count": accepted_count, "applications": accepted_s.data},
        "rejected": {"count": rejected_data.count(), "applications": rejected.data},
        "pending": {"count": pending_data.count(), "applications": pending.data},
        "inprogress": {"count": inprogress_data.count(), "applications": inprogress.data},
    }
    return JsonResponse({"status": "success", "data": data})
