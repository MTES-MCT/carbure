from core.decorators import check_rights
from core.models import EntityDepot
from django.http import JsonResponse


@check_rights("entity_id")
def get_depots(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
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
