from django.http import JsonResponse

from core.decorators import check_user_rights
from core.models import UserRights, UserRightsRequests


@check_user_rights(role=[UserRights.ADMIN])
def accept_user(request, entity, entity_id):
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
