from django.http import JsonResponse

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.decorators import check_user_rights
from core.models import CarbureLot, EntityDepot, UserRights


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def delete_depot(request, entity, entity_id):
    delivery_site_id = request.POST.get("delivery_site_id", False)

    try:
        EntityDepot.objects.filter(entity=entity, depot__depot_id=delivery_site_id).delete()
        lots = CarbureLot.objects.filter(carbure_client=entity, carbure_delivery_site__depot_id=delivery_site_id)
        background_bulk_scoring(lots)
        background_bulk_sanity_checks(lots)
    except Exception:
        return JsonResponse(
            {
                "status": "error",
                "message": "Could not delete entity's delivery site",
            },
            status=400,
        )

    return JsonResponse({"status": "success"})
