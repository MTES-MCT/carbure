from django.http.response import JsonResponse
from audit.helpers import get_auditor_lots_by_status

from core.decorators import check_user_rights, is_auditor
from api.v4.helpers import (
    get_lots_filters_data,
)

from core.models import (
    Entity,
)


@check_user_rights()
@is_auditor
def get_lots_filters(request, *args, **kwargs):
    status = request.GET.get("status", False)
    field = request.GET.get("field", False)
    entity_id = request.GET.get("entity_id", False)
    if not field:
        return JsonResponse(
            {
                "status": "error",
                "message": "Please specify the field for which you want the filters",
            },
            status=400,
        )
    entity = Entity.objects.get(id=entity_id)
    lots = get_auditor_lots_by_status(entity, status, request)
    data = get_lots_filters_data(lots, request.GET, entity, field)
    if data is None:
        return JsonResponse(
            {"status": "error", "message": "Could not find specified filter"},
            status=400,
        )
    else:
        return JsonResponse({"status": "success", "data": data})
