from core.decorators import check_user_rights
from core.models import Entity, UserRights
from django.http import JsonResponse


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def set_preferred_unit(request, *args, **kwargs):
    entity_id = kwargs["context"]["entity_id"]
    unit = request.POST.get("unit", "l")
    entity = Entity.objects.get(id=entity_id)
    entity.preferred_unit = unit
    entity.save()
    return JsonResponse({"status": "success"})
