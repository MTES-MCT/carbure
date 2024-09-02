from django.http import JsonResponse

from core.decorators import check_user_rights
from core.models import EntityDepot


@check_user_rights()
def get_depots(request, entity, entity_id):
    try:
        ds = EntityDepot.objects.filter(entity=entity)
        ds = [d.natural_key() for d in ds]
    except Exception:
        return JsonResponse(
            {
                "status": "error",
                "message": "Could not find entity's delivery sites",
            },
            status=400,
        )
    return JsonResponse({"status": "success", "data": ds})
