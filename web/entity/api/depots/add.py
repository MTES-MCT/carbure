import traceback

from django.http import JsonResponse

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.carburetypes import CarbureSanityCheckErrors
from core.decorators import check_user_rights
from core.models import CarbureLot, Entity, GenericError, UserRights
from transactions.models import EntitySite
from transactions.models import Site as Depot


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def add_depot(request, entity, entity_id):
    delivery_site_id = request.POST.get("delivery_site_id", False)
    ownership_type = request.POST.get("ownership_type", False)

    blending_is_outsourced = request.POST.get("blending_outsourced", False)
    if blending_is_outsourced == "true":
        blending_is_outsourced = True
    else:
        blending_is_outsourced = False
    blending_entity_id = request.POST.get("blending_entity_id", False)

    if not delivery_site_id:
        return JsonResponse({"status": "error", "message": "Missing delivery site id"}, status=400)
    if not ownership_type:
        return JsonResponse({"status": "error", "message": "Missing ownership type"}, status=400)

    try:
        ds = Depot.objects.get(customs_id=delivery_site_id)
    except Exception:
        return JsonResponse(
            {
                "status": "error",
                "message": "Could not find delivery site",
            },
            status=400,
        )

    blender = None
    if blending_is_outsourced:
        try:
            blender = Entity.objects.get(id=blending_entity_id, entity_type=Entity.OPERATOR)
        except Exception:
            return JsonResponse({"status": "error", "message": "Could not find outsourcing blender"}, status=400)

    try:
        ed, created = EntitySite.objects.update_or_create(
            entity=entity,
            site=ds,
            defaults={
                "ownership_type": ownership_type,
                "blending_is_outsourced": blending_is_outsourced,
                "blender": blender,
            },
        )
        lots = CarbureLot.objects.filter(carbure_client=entity, carbure_delivery_site=ds)
        background_bulk_scoring(lots)
        background_bulk_sanity_checks(lots)
        GenericError.objects.filter(lot__in=lots, error=CarbureSanityCheckErrors.DEPOT_NOT_CONFIGURED).delete()
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {
                "status": "error",
                "message": "Could not link entity to delivery site",
            },
            status=400,
        )
    return JsonResponse({"status": "success"})
