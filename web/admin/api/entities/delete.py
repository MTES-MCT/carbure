from django.http import JsonResponse
from core.decorators import is_admin
from core.models import Entity


@is_admin
def delete_entity(request):
    entity_id = request.POST.get("entity_id", False)

    if not entity_id:
        return JsonResponse({"status": "error", "message": "Please provide an entity_id"}, status=400)
    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find entity"}, status=400)

    entity.delete()
    return JsonResponse({"status": "success", "data": "success"})
