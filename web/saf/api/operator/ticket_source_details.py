# /api/saf/operator/ticket-sources/details

import traceback

from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicketSource
from saf.serializers import SafTicketSourceDetailsSerializer


class SafTicketSourceDetailsError:
    TICKET_SOURCE_DETAILS_FAILED = "TICKET_SOURCE_DETAILS_FAILED"
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


@check_user_rights()
def get_ticket_source_details(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
        ticket_source_id = int(request.GET.get("ticket_source_id"))
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketSourceDetailsError.MALFORMED_PARAMS)

    try:
        ticket_source = (
            SafTicketSource.objects.prefetch_related("saf_tickets")
            .prefetch_related("saf_tickets__client")
            .get(id=ticket_source_id, added_by_id=entity_id)
        )

        serialized = SafTicketSourceDetailsSerializer(ticket_source)
        return SuccessResponse(serialized.data)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketSourceDetailsError.TICKET_SOURCE_DETAILS_FAILED)
