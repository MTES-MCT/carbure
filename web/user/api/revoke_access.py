from core.decorators import check_user_rights
from core.models import UserRights, UserRightsRequests
from django.http import JsonResponse


@check_user_rights()
def revoke_myself(request, entity, entity_id):
    try:
        right = UserRights.objects.get(user=request.user, entity_id=entity_id)
        right.delete()
    except:
        pass

    try:
        rr = UserRightsRequests.objects.get(user=request.user, entity_id=entity_id)
        rr.delete()
    except Exception:
        pass
    return JsonResponse({"status": "success"})
