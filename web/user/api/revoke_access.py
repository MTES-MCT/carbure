from core.decorators import otp_or_403
from core.models import UserRights
from django.http import JsonResponse


@otp_or_403
def revoke_myself(request, *args, **kwargs):
    entity_id = request.POST.get("entity_id", False)

    if not entity_id:
        return JsonResponse({"status": "error", "message": "Missing entity ID"})

    try:
        right = UserRights.objects.get(user=request.user, entity_id=entity_id)
        right.delete()
    except:
        pass

    return JsonResponse({"status": "success"})
