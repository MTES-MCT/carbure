# /api/saf/operator/snapshot

import traceback
from datetime import datetime

from django.db.models.query_utils import Q

from certificates.models import DoubleCountingRegistration
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from doublecount.models import DoubleCountingApplication


class SafSnapshotError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    SNAPSHOT_FAILED = "SNAPSHOT_FAILED"


@check_admin_rights(allow_external=[ExternalAdminRights.DOUBLE_COUNTING])
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
        agreements_incoming = DoubleCountingRegistration.objects.filter(Q(valid_from__year__gt=current_year))
        agreements_active = DoubleCountingRegistration.objects.filter(
            Q(valid_from__year__lte=current_year) & Q(valid_until__year__gte=current_year)
        )
        agreements_expired = DoubleCountingRegistration.objects.filter(Q(valid_until__year__lt=current_year))
        # agreements_active = DoubleCountingRegistration.objects.filter((Q(period_start__year=year) | Q(period_end__year=year)))  # noqa: E501
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
