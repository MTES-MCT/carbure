# /api/v5/saf/ticket-s

from math import floor
import traceback
from django.core.paginator import Paginator

from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicket
from saf.serializers import SafTicketSerializer


class SafTicketError:
    TICKET_LISTING_FAILED = "TICKET_LISTING_FAILED"
    FILTERS_MALFORMED = "FILTERS_MALFORMED"


@check_user_rights()
def get_tickets(request, *args, **kwargs):
    entity_id = int(kwargs["context"]["entity_id"])

    try:
        year = int(request.GET.get("year"))
        status = request.GET["status"]
        from_idx = int(request.GET.get("from_idx", 0))
        limit = int(request.GET.get("limit", 25))
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketError.FILTERS_MALFORMED)

    try:
        tickets = SafTicket.objects.filter(status=status, year=year, supplier_id=entity_id).select_related(
            "parent_ticket_source"
        )

        paginator = Paginator(tickets, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)

        ids = tickets.values_list("id", flat=True)
        serialized = SafTicketSerializer(page.object_list, many=True)

        return SuccessResponse(
            {
                "saf_tickets": serialized.data,
                "ids": list(ids),
                "from": from_idx,
                "returned": len(serialized.data),
                "total": len(ids),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketError.TICKET_LISTING_FAILED)
