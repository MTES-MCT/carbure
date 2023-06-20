from django.db.models.query_utils import Q

from django.http import JsonResponse
from core.decorators import is_admin_or_external_admin

from doublecount.models import (
    DoubleCountingAgreement,
)
from doublecount.serializers import DoubleCountingAgreementFullSerializer


@is_admin_or_external_admin
def get_agreements_admin(request):
    year = request.GET.get("year", False)
    if not year:
        return JsonResponse({"status": "error", "message": "Missing year"}, status=400)

    agreements = DoubleCountingAgreement.objects.filter(Q(period_start__year=year) | Q(period_end__year=year))
    accepted = agreements.filter(status=DoubleCountingAgreement.ACCEPTED)
    accepted_count = accepted.count()
    rejected = agreements.filter(status=DoubleCountingAgreement.REJECTED)
    rejected_count = rejected.count()
    expired = agreements.filter(status=DoubleCountingAgreement.LAPSED)
    expired_count = expired.count()
    pending = agreements.filter(status=DoubleCountingAgreement.PENDING)
    pending_count = pending.count()
    progress = agreements.filter(status=DoubleCountingAgreement.INPROGRESS)
    progress_count = progress.count()

    accepted_s = DoubleCountingAgreementFullSerializer(accepted, many=True)
    rejected_s = DoubleCountingAgreementFullSerializer(rejected, many=True)
    expired_s = DoubleCountingAgreementFullSerializer(expired, many=True)
    pending_s = DoubleCountingAgreementFullSerializer(pending, many=True)
    progress_s = DoubleCountingAgreementFullSerializer(progress, many=True)
    data = {
        "accepted": {"count": accepted_count, "agreements": accepted_s.data},
        "rejected": {"count": rejected_count, "agreements": rejected_s.data},
        "expired": {"count": expired_count, "agreements": expired_s.data},
        "progress": {"count": progress_count, "agreements": progress_s.data},
        "pending": {"count": pending_count, "agreements": pending_s.data},
    }
    return JsonResponse({"status": "success", "data": data})
