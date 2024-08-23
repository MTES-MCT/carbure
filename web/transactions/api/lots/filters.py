from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.helpers import (
    get_entity_lots_by_status,
    get_lots_filters_data,
)
from core.models import (
    Entity,
)


@check_user_rights()
def get_lots_filters(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.GET.get("status", False)
    field = request.GET.get("field", False)
    if not field:
        return JsonResponse(
            {
                "status": "error",
                "message": "Please specify the field for which you want the filters",
            },
            status=400,
        )
    entity = Entity.objects.get(id=entity_id)
    txs = get_entity_lots_by_status(entity, status)
    data = get_lots_filters_data(txs, request.GET, entity, field)
    if data is None:
        return JsonResponse(
            {"status": "error", "message": "Could not find specified filter"},
            status=400,
        )
    else:
        return JsonResponse({"status": "success", "data": data})
