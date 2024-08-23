from django.http import JsonResponse

from core.decorators import check_user_rights
from core.models import Entity, UserRights


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def toggle_release_for_consumption(request, *args, **kwargs):
    has_mac = request.POST.get("has_mac", "false")
    entity_id = kwargs["context"]["entity_id"]
    entity = Entity.objects.get(id=entity_id)
    entity.has_mac = True if has_mac == "true" else False
    entity.save()
    return JsonResponse({"status": "success"})
