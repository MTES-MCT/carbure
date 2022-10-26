# /api/v5/saf/tickets

from math import floor
import traceback
from django.core.paginator import Paginator

from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicket
from saf.serializers import SafTicketSerializer
from core.models import Entity
from django.contrib.auth.decorators import login_required


class SafClientsError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


@login_required
def get_clients(request, *args, **kwargs):
    try:
        q = request.GET.get('query', False)
        # TODO Entity.AIRLINE
        entities = Entity.objects.filter(entity_type=Entity.PRODUCER).order_by('name')
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafClientsError.MALFORMED_PARAMS)

    if q:
        entities = entities.filter(name__icontains=q)
    sez = [{'entity_type': e.entity_type, 'name': e.name, 'id': e.id} for e in entities]
    #     serialized = SafTicketSerializer(page.object_list, many=True)

    return SuccessResponse({'status': 'success', 'data': sez})
    # try:
    #     entity_id = int(kwargs["context"]["entity_id"])
    #     year = int(request.GET.get("year"))
    #     status = request.GET["status"]
    #     from_idx = int(request.GET.get("from_idx", 0))
    #     limit = int(request.GET.get("limit", 25))
    # except:
    #     traceback.print_exc()
    #     return ErrorResponse(400, SafTicketError.MALFORMED_PARAMS)

    # try:
    #     tickets = SafTicket.objects.filter(status=status, year=year, supplier_id=entity_id).select_related(
    #         "parent_ticket_source"
    #     )

    #     paginator = Paginator(tickets, limit)
    #     current_page = floor(from_idx / limit) + 1
    #     page = paginator.page(current_page)

    #     ids = tickets.values_list("id", flat=True)
    #     serialized = SafTicketSerializer(page.object_list, many=True)

    #     return SuccessResponse(
    #         {
    #             "saf_tickets": serialized.data,
    #             "ids": list(ids),
    #             "from": from_idx,
    #             "returned": len(serialized.data),
    #             "total": len(ids),
    #         }
    #     )
    # except Exception:
    #     traceback.print_exc()
    #     return ErrorResponse(400, SafTicketError.TICKET_LISTING_FAILED)
