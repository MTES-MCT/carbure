from django.http import JsonResponse

from core.decorators import check_admin_rights
from transactions.models import Depot, EntitySite


@check_admin_rights()
def get_entity_depots(request):
    company_id = request.GET.get("company_id", False)

    try:
        ds = EntitySite.objects.filter(entity=company_id, site__in=Depot.objects.filter(is_enabled=True))
        ds = [d.natural_key() for d in ds]
        return JsonResponse({"status": "success", "data": ds})
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find Entity Depots"}, status=400)
