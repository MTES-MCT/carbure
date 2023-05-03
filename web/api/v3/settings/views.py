from core.decorators import check_rights, otp_or_403
from django.http import JsonResponse


@otp_or_403
@check_rights("entity_id")
def get_entity_hash(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
    return JsonResponse({"status": "success", "data": {"hash": entity.hash}})
