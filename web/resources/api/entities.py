from django.http import JsonResponse

from core.models import Entity


def get_entities(request):
    q = request.GET.get("query", False)
    entity_type = request.GET.getlist("entity_type")
    entities = Entity.objects.all().order_by("name")
    if q:
        entities = entities.filter(name__icontains=q)
    if entity_type:
        entities = entities.filter(entity_type__in=entity_type)
    sez = [{"entity_type": e.entity_type, "name": e.name, "id": e.id} for e in entities]
    return JsonResponse({"status": "success", "data": sez})
