# /api/v5/saf/snapshot

import traceback
from django.db.models.expressions import F
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicketSource, SafTicket


class SafSnapshotError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    SNAPSHOT_FAILED = "SNAPSHOT_FAILED"


@check_user_rights()
def get_snapshot(request, *args, **kwargs):

    try:
        entity_id = int(kwargs["context"]["entity_id"])
        year = int(request.GET.get("year"))
    except:
        return ErrorResponse(400, SafSnapshotError.PARAMS_MALFORMED)

    print(tickets)
    try:
        sources = SafTicketSource.objects.filter(year=year, added_by_id=entity_id)
        tickets = SafTicket.objects.filter(year=year, supplier_id=entity_id)
        return SuccessResponse(
            {
                "ticket_sources_available": sources.filter(assigned_volume__lt=F("total_volume")).count(),
                "ticket_sources_history": sources.filter(assigned_volume=F("total_volume")).count(),
                "tickets": tickets.count(),
                "tickets_pending": tickets.filter(status=SafTicket.PENDING).count(),
                "tickets_accepted": tickets.filter(status=SafTicket.ACCEPTED).count(),
                "tickets_rejected": tickets.filter(status=SafTicket.REJECTED).count(),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafSnapshotError.SNAPSHOT_FAILED)
