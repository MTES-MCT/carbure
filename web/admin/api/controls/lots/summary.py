import traceback
from admin.api.controls.helpers import get_admin_summary_data

from admin.helpers import get_admin_lots_by_status
from core.helpers import (
    filter_lots,
)
from core.decorators import is_admin
from core.models import (
    Entity,
)
from django.http.response import JsonResponse


@is_admin
def get_lots_summary(request, *args, **kwargs):
    status = request.GET.get("status", False)
    short = request.GET.get("short", False)
    entity_id = request.GET.get("entity_id", False)
    if not status:
        return JsonResponse(
            {"status": "error", "message": "Missing status"}, status=400
        )
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_admin_lots_by_status(entity, status)
        lots = filter_lots(lots, request.GET, entity, will_aggregate=True)
        summary = get_admin_summary_data(lots, short == "true")
        return JsonResponse({"status": "success", "data": summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get lots summary"}, status=400
        )
