from core.decorators import check_user_rights, otp_or_403
from core.models import UserRights, Entity
from django.http import JsonResponse


@otp_or_403
@check_user_rights(role=[UserRights.ADMIN])
def accept_user(request, *args, **kwargs):
    entity_id = kwargs["context"]["entity_id"]
    entity = Entity.objects.get(id=entity_id)

    request_id = request.POST.get("request_id", None)

    if request_id is None:
        return JsonResponse({"status": "error", "message": "Missing request_id"}, status=400)

    try:
        right = UserRights.objects.get(id=request_id, entity=entity)
        right.status = "ACCEPTED"
        right.save()
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not create rights"}, status=400)
    return JsonResponse({"status": "success"})
