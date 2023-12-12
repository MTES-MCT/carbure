# /api/saf/airline/snapshot

import traceback
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicket


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
    try:
        tickets = SafTicket.objects.filter(year=year, client_id=entity_id)
        return SuccessResponse(
            {
                "tickets_pending": tickets.filter(status=SafTicket.PENDING).count(),
                "tickets_accepted": tickets.filter(status=SafTicket.ACCEPTED).count(),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafSnapshotError.SNAPSHOT_FAILED)
