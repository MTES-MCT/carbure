from core.decorators import check_user_rights, otp_or_403
from core.models import UserRights, Entity
from django.contrib.auth import get_user_model
from django.http import JsonResponse


@otp_or_403
@check_user_rights()
def get_entity_rights(request, *args, **kwargs):
    entity_id = kwargs["context"]["entity_id"]
    entity = Entity.objects.get(id=entity_id)

    rights = UserRights.objects.filter(entity=entity, status__in=["PENDING", "ACCEPTED"])

    data = {}
    data["rights"] = [r.natural_key() for r in rights]
    return JsonResponse({"status": "success", "data": data})
