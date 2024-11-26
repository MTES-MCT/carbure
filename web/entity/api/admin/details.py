from django.http import JsonResponse

from core.decorators import check_admin_rights
from core.models import Entity, ExternalAdminRights


@check_admin_rights(
    allow_external=[ExternalAdminRights.AIRLINE, ExternalAdminRights.ELEC, ExternalAdminRights.DOUBLE_COUNTING]
)
def get_entity_details(request):
    company_id = request.GET.get("company_id", False)

    try:
        e = Entity.objects.get(pk=company_id)
        return JsonResponse({"status": "success", "data": e.natural_key()})
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find entity"}, status=400)
