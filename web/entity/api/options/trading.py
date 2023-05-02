from core.decorators import check_user_rights
from core.models import UserRights, Entity
from django.http import JsonResponse


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def toggle_trading(request, *args, **kwargs):
    entity_id = kwargs["context"]["entity_id"]
    entity = Entity.objects.get(id=entity_id)
    has_trading = request.POST.get("has_trading", "false")
    entity.has_trading = True if has_trading == "true" else False
    entity.save()
    return JsonResponse({"status": "success"})
