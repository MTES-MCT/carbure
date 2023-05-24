from core.common import (
    ErrorResponse,
    SuccessResponse,
)
from core.decorators import check_user_rights
from core.helpers import (
    get_prefetched_data,
)

from core.models import (
    CarbureLot,
)


@check_user_rights()
def recalc_score(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_id = request.POST.get("lot_id")
    prefetched_data = get_prefetched_data()
    try:
        lot = CarbureLot.objects.get(id=lot_id)
        lot.recalc_reliability_score(prefetched_data)
        lot.save()
    except:
        return ErrorResponse(404)
    return SuccessResponse()
