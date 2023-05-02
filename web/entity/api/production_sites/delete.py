from core.decorators import check_rights
from core.models import CarbureLot, UserRights
from django.http import JsonResponse
from producers.models import ProductionSite


@check_rights("entity_id", role=[UserRights.ADMIN])
def delete_production_site(request, *args, **kwargs):
    site = request.POST.get("production_site_id")
    context = kwargs["context"]
    entity = context["entity"]

    try:
        ps = ProductionSite.objects.get(id=site, producer=entity)
    except Exception as e:
        print(e)
        return JsonResponse({"status": "error", "message": "Unknown Production Site"}, status=400)

    # make sure there is no impact by deleting this
    lots = CarbureLot.objects.filter(
        carbure_production_site=ps, lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN]
    )
    if lots.count() > 0:
        msg = "Validated lots associated with this production site. Cannot delete"
        return JsonResponse({"status": "error", "message": msg}, status=400)
    ps.delete()
    return JsonResponse({"status": "success"})
