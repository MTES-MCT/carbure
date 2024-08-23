# /api/saf/airline/years

import traceback

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from saf.models import SafTicket


class SafYearsError:
    YEAR_LISTING_FAILED = "YEAR_LISTING_FAILED"


@check_user_rights()
def get_years(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
        ticket_years = SafTicket.objects.filter(client_id=entity_id).values_list("year", flat=True).distinct()
        years = sorted(set(ticket_years))
        return SuccessResponse(years)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafYearsError.YEAR_LISTING_FAILED)
