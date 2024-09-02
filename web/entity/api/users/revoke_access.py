from django.contrib.auth import get_user_model
from django.http import JsonResponse

from core.decorators import check_user_rights
from core.models import UserRights, UserRightsRequests


@check_user_rights(role=[UserRights.ADMIN])
def revoke_user(request, entity, entity_id):
    email = request.POST.get("email", None)
    user_model = get_user_model()

    try:
        user = user_model.objects.get(email=email)
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find user"}, status=400)

    try:
        UserRights.objects.filter(user=user, entity=entity).delete()
    except Exception:
        pass
    try:
        rr = UserRightsRequests.objects.get(user=user, entity=entity)
        rr.status = "REVOKED"
        rr.save()
    except Exception:
        pass

    return JsonResponse({"status": "success"})
