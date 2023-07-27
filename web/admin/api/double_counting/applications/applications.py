from django.db.models.query_utils import Q

from django.http import JsonResponse
from core.decorators import is_admin_or_external_admin

from doublecount.models import (
    DoubleCountingApplication,
)
from doublecount.serializers import DoubleCountingApplicationFullSerializer


@is_admin_or_external_admin
def get_applications_admin(request):
    year = request.GET.get("year", False)
    if not year:
        return JsonResponse({"status": "error", "message": "Missing year"}, status=400)

    applications = DoubleCountingApplication.objects.filter(Q(period_start__year=year) | Q(period_end__year=year))
    accepted = applications.filter(status=DoubleCountingApplication.ACCEPTED)
    accepted_count = accepted.count()
    rejected = applications.filter(status=DoubleCountingApplication.REJECTED)
    rejected_count = rejected.count()
    expired = applications.filter(status=DoubleCountingApplication.LAPSED)
    expired_count = expired.count()
    pending = applications.filter(status=DoubleCountingApplication.PENDING)
    pending_count = pending.count()
    progress = applications.filter(status=DoubleCountingApplication.INPROGRESS)
    progress_count = progress.count()

    accepted_s = DoubleCountingApplicationFullSerializer(accepted, many=True)
    rejected_s = DoubleCountingApplicationFullSerializer(rejected, many=True)
    expired_s = DoubleCountingApplicationFullSerializer(expired, many=True)
    pending_s = DoubleCountingApplicationFullSerializer(pending, many=True)
    progress_s = DoubleCountingApplicationFullSerializer(progress, many=True)
    data = {
        "accepted": {"count": accepted_count, "applications": accepted_s.data},
        "rejected": {"count": rejected_count, "applications": rejected_s.data},
        "expired": {"count": expired_count, "applications": expired_s.data},
        "progress": {"count": progress_count, "applications": progress_s.data},
        "pending": {"count": pending_count, "applications": pending_s.data},
    }
    return JsonResponse({"status": "success", "data": data})
