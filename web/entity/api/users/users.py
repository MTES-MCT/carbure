from core.decorators import check_user_rights, otp_or_403
from core.models import UserRights, UserRightsRequests, Entity
from django.http import JsonResponse


@otp_or_403
@check_user_rights()
def get_entity_rights(request, *args, **kwargs):
    entity_id = kwargs["context"]["entity_id"]
    entity = Entity.objects.get(id=entity_id)

    rights = UserRights.objects.filter(entity=entity)
    requests = UserRightsRequests.objects.filter(entity=entity, status__in=["PENDING", "ACCEPTED"])

    # hide users of the Carbure staff
    if not request.user.is_staff:
        rights = rights.filter(user__is_staff=False, user__is_superuser=False)
        requests = requests.filter(user__is_staff=False, user__is_superuser=False)

    data = {}
    data["rights"] = [r.natural_key() for r in rights]
    data["requests"] = [r.natural_key() for r in requests]
    return JsonResponse({"status": "success", "data": data})
