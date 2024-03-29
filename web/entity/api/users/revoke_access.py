from core.decorators import check_user_rights, otp_or_403
from core.models import UserRights, UserRightsRequests, Entity
from django.http import JsonResponse
from django.contrib.auth import get_user_model


@otp_or_403
@check_user_rights(role=[UserRights.ADMIN])
def revoke_user(request, *args, **kwargs):
    entity_id = kwargs["context"]["entity_id"]
    entity = Entity.objects.get(id=entity_id)
    email = request.POST.get("email", None)
    user_model = get_user_model()

    try:
        user = user_model.objects.get(email=email)
    except:
        return JsonResponse({"status": "error", "message": "Could not find user"}, status=400)

    try:
        UserRights.objects.filter(user=user, entity=entity).delete()
    except:
        pass
    try:
        rr = UserRightsRequests.objects.get(user=user, entity=entity)
        rr.status = "REVOKED"
        rr.save()
    except:
        pass

    return JsonResponse({"status": "success"})
