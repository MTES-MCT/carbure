import traceback

from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.helpers import (
    filter_lots,
    get_entity_lots_by_status,
    get_lots_summary_data,
)
from core.models import (
    Entity,
)


@check_user_rights()
def get_lots_summary(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.GET.get("status", False)
    short = request.GET.get("short", False) == "true"
    if not status:
        return JsonResponse(
            {"status": "error", "message": "Missing status"}, status=400
        )
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_entity_lots_by_status(entity, status)
        lots = filter_lots(lots, request.GET, entity, will_aggregate=True)
        summary = get_lots_summary_data(lots, entity, short)
        return JsonResponse({"status": "success", "data": summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get lots summary"}, status=400
        )
