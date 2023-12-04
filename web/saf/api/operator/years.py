# /api/v5/saf/operator/years

import traceback
from django.db.models import Q
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from saf.models import SafTicketSource, SafTicket


class SafYearsError:
    YEAR_LISTING_FAILED = "YEAR_LISTING_FAILED"


@check_user_rights()
def get_years(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
        ticket_source_years = SafTicketSource.objects.filter(added_by_id=entity_id).values_list("year", flat=True).distinct()
        client_or_supplier = Q(supplier_id=entity_id) | Q(client_id=entity_id)
        ticket_years = SafTicket.objects.filter(client_or_supplier).values_list("year", flat=True).distinct()
        years = sorted(set(list(ticket_source_years) + list(ticket_years)))
        return SuccessResponse(years)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafYearsError.YEAR_LISTING_FAILED)
