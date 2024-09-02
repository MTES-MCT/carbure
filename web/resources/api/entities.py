from django.http import JsonResponse

from core.models import Entity


def get_entities(request):
    q = request.GET.get("query", False)
    entities = Entity.objects.all().order_by("name")
    if q:
        entities = entities.filter(name__icontains=q)
    sez = [{"entity_type": e.entity_type, "name": e.name, "id": e.id} for e in entities]
    return JsonResponse({"status": "success", "data": sez})
