import traceback

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.carburetypes import CarbureSanityCheckErrors
from core.decorators import check_rights
from core.models import CarbureLot, Depot, Entity, EntityDepot, GenericError, UserRights
from django.http import JsonResponse


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def add_depot(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
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
        ds = Depot.objects.get(depot_id=delivery_site_id)
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
        except:
            return JsonResponse({"status": "error", "message": "Could not find outsourcing blender"}, status=400)

    try:
        ed, created = EntityDepot.objects.update_or_create(
            entity=entity,
            depot=ds,
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
