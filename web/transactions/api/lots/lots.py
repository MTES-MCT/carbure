import traceback

from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.helpers import (
    get_entity_lots_by_status,
    get_lots_with_metadata,
)
from core.models import (
    Entity,
)


@check_user_rights()
def get_lots(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.GET.get("status", False)
    selection = request.GET.get("selection", False)
    export = request.GET.get("export", False)
    if not status and not selection:
        return JsonResponse(
            {"status": "error", "message": "Missing status"}, status=400
        )
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_entity_lots_by_status(entity, status, export)
        return get_lots_with_metadata(lots, entity, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get lots"}, status=400
        )
