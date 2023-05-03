from core.decorators import check_user_rights, otp_or_403
from core.models import UserRights, UserRightsRequests, Entity
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
        right_request = UserRightsRequests.objects.get(id=request_id, entity=entity)
        right_request.status = "ACCEPTED"
        UserRights.objects.update_or_create(
            user=right_request.user,
            entity=entity,
            defaults={"role": right_request.role, "expiration_date": right_request.expiration_date},
        )
        right_request.save()
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not create rights"}, status=400)
    return JsonResponse({"status": "success"})
