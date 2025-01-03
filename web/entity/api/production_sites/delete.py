from django.http import JsonResponse

from core.decorators import check_user_rights
from core.models import CarbureLot, UserRights
from transactions.models import ProductionSite


@check_user_rights(role=[UserRights.ADMIN])
def delete_production_site(request, entity, entity_id):
    site = request.POST.get("production_site_id")

    try:
        ps = ProductionSite.objects.get(id=site, created_by=entity)
    except Exception as e:
        print(e)
        return JsonResponse({"status": "error", "message": "Unknown Production Site"}, status=400)

    # make sure there is no impact by deleting this
    lots = CarbureLot.objects.filter(carbure_production_site=ps, lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN])
    if lots.count() > 0:
        msg = "Validated lots associated with this production site. Cannot delete"
        return JsonResponse({"status": "error", "message": msg}, status=400)
    ps.delete()
    return JsonResponse({"status": "success"})
