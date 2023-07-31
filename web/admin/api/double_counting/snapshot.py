# /api/v5/saf/operator/snapshot

import traceback
from django.db.models.expressions import F
from certificates.models import DoubleCountingRegistration
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from doublecount.models import DoubleCountingApplication
from saf.models import SafTicketSource, SafTicket
from django.db.models.query_utils import Q
from datetime import datetime


class SafSnapshotError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    SNAPSHOT_FAILED = "SNAPSHOT_FAILED"


@check_user_rights()
def get_snapshot(request, *args, **kwargs):
    current_year = datetime.now().year

    try:
        applications = DoubleCountingApplication.objects.filter()

        applications_pending = applications.filter(
            ~Q(status__in=[DoubleCountingApplication.ACCEPTED, DoubleCountingApplication.REJECTED])
        )
        applications_rejected = applications.filter(Q(status=DoubleCountingApplication.REJECTED))

        # agreements_expired_soon = DoubleCountingRegistration.objects.filter(
        #     Q(valid_from__year__lte=current_year) & Q(valid_until__year__gte=current_year)
        # )
        agreements_incoming = DoubleCountingRegistration.objects.filter(Q(valid_from__year__lt=current_year))
        agreements_active = DoubleCountingRegistration.objects.filter(
            Q(valid_from__year__lte=current_year) & Q(valid_until__year__gte=current_year)
        )
        agreements_expired = DoubleCountingRegistration.objects.filter(Q(valid_until__year__lt=current_year))
        # agreements_active = DoubleCountingRegistration.objects.filter((Q(period_start__year=year) | Q(period_end__year=year)))
        # TODO  agreements_torenew

        return SuccessResponse(
            {
                # "applications": applications_pending.count(),
                "applications_pending": applications_pending.count(),
                "applications_rejected": applications_rejected.count(),
                # "agreements": agreements_active.count(),
                "agreements_incoming": agreements_incoming.count(),
                "agreements_active": agreements_active.count(),
                "agreements_expired": agreements_expired.count(),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafSnapshotError.SNAPSHOT_FAILED)
