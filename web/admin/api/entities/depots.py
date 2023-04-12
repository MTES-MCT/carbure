from django.http import JsonResponse
from core.decorators import check_admin_rights
from core.models import Entity


@check_admin_rights()
def get_entity_depots(request):
    entity_id = request.GET.get("entity_id", False)

    try:
        e = Entity.objects.get(pk=entity_id)
        data = [ps.natural_key() for ps in e.entitydepot_set.all()]
        return JsonResponse({"status": "success", "data": data})
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find Entity Depots"}, status=400)
