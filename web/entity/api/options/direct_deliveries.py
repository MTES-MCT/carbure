from core.decorators import check_user_rights
from core.models import UserRights, Entity
from django.http import JsonResponse


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def toggle_direct_deliveries(request, *args, **kwargs):
    entity_id = kwargs["context"]["entity_id"]
    entity = Entity.objects.get(id=entity_id)
    has_direct_deliveries = request.POST.get("has_direct_deliveries", "false")
    entity.has_direct_deliveries = True if has_direct_deliveries == "true" else False
    entity.save()
    return JsonResponse({"status": "success"})
