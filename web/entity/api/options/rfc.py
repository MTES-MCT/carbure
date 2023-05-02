from core.decorators import check_user_rights, otp_or_403
from core.models import Entity, UserRights, UserRightsRequests
from django.contrib.auth import get_user_model
from django.http import JsonResponse


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def toggle_rfc(request, *args, **kwargs):
    has_mac = request.POST.get("has_mac", "false")
    entity_id = kwargs["context"]["entity_id"]
    entity = Entity.objects.get(id=entity_id)
    entity.has_mac = True if has_mac == "true" else False
    entity.save()
    return JsonResponse({"status": "success"})
