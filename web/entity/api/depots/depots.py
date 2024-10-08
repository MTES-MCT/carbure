from django.http import JsonResponse

from core.decorators import check_user_rights
from transactions.models import Depot, EntitySite


@check_user_rights()
def get_depots(request, entity, entity_id):
    try:
        ds = EntitySite.objects.filter(entity=entity)
        ds = [d.natural_key() for d in ds if d.site.site_type != Depot.PRODUCTION_SITE]
    except Exception:
        return JsonResponse(
            {
                "status": "error",
                "message": "Could not find entity's delivery sites",
            },
            status=400,
        )
    return JsonResponse({"status": "success", "data": ds})
