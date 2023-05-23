import traceback

from admin.helpers import get_admin_lots_by_status
from api.v4.helpers import (
    get_lots_with_metadata,
)
from core.decorators import is_admin
from core.models import (
    Entity,
)
from django.http.response import JsonResponse


@is_admin
def get_lots(request, *args, **kwargs):
    status = request.GET.get("status", False)
    selection = request.GET.get("selection", False)
    entity_id = request.GET.get("entity_id", False)
    export = request.GET.get("export", False)
    if not status and not selection:
        return JsonResponse(
            {"status": "error", "message": "Missing status"}, status=400
        )
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_admin_lots_by_status(entity, status, export)
        return get_lots_with_metadata(lots, entity, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get lots"}, status=400
        )
