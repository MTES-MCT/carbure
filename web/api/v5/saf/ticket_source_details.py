# /api/v5/saf/ticket-sources/details

from math import floor
import traceback
from django.core.paginator import Paginator

from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicketSource
from saf.serializers import SafTicketSourceDetailsSerializer


class SafTicketSourceError:
    TICKET_SOURCE_LISTING_FAILED = "TICKET_SOURCE_LISTING_FAILED"
    FILTERS_MALFORMED = "FILTERS_MALFORMED"


@check_user_rights()
def get_ticket_source_details(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
        ticket_source_id = int(request.GET.get("ticket_source_id"))
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketSourceError.FILTERS_MALFORMED)

    try:
        ticket_source = (
            SafTicketSource.objects.prefetch_related("saf_tickets")
            .prefetch_related("saf_tickets__client")
            .get(id=ticket_source_id, added_by_id=entity_id)
        )

        serialized = SafTicketSourceDetailsSerializer(ticket_source)

        print(serialized.data)

        return SuccessResponse(serialized.data)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketSourceError.TICKET_SOURCE_LISTING_FAILED)
