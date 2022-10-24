# /api/v5/saf/ticket-sources

from math import floor
import traceback
from django.core.paginator import Paginator

from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicketSource
from saf.serializers import SafTicketSourceSerializer


class SafTicketSourceError:
    TICKET_SOURCE_LISTING_FAILED = "TICKET_SOURCE_LISTING_FAILED"
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


@check_user_rights()
def get_ticket_sources(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
        year = int(request.GET.get("year"))
        status = request.GET.get("status")
        from_idx = int(request.GET.get("from_idx", 0))
        limit = int(request.GET.get("limit", 25))
    except:
        return ErrorResponse(400, SafTicketSourceError.MALFORMED_PARAMS)

    try:
        ticket_sources = (
            SafTicketSource.objects.filter(year=year, added_by_id=entity_id)
            .prefetch_related("saf_tickets")
            .prefetch_related("saf_tickets__client")
        )

        paginator = Paginator(ticket_sources, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)

        ids = ticket_sources.values_list("id", flat=True)
        print(ids)
        serialized = SafTicketSourceSerializer(page.object_list, many=True)

        return SuccessResponse(
            {
                "saf_ticket_sources": serialized.data,
                "ids": list(ids),
                "from": from_idx,
                "returned": len(serialized.data),
                "total": len(ids),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketSourceError.TICKET_SOURCE_LISTING_FAILED)
