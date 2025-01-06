from django.http import JsonResponse

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.decorators import check_user_rights
from core.models import Biocarburant, CarbureLot, GenericError, UserRights
from producers.models import ProductionSiteOutput
from transactions.models import ProductionSite


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def set_production_site_biofuels(request, entity, entity_id):
    site = request.POST.get("production_site_id")
    bc_list = request.POST.getlist("biocarburant_codes")

    if site is None:
        return JsonResponse({"status": "error", "message": "Missing production_site_id"}, status=400)
    if bc_list is None:
        return JsonResponse({"status": "error", "message": "Missing biocarburant_codes"}, status=400)

    try:
        bc_list = Biocarburant.objects.filter(code__in=bc_list)
    except Exception:
        return JsonResponse({"status": "error", "message": "Unknown BC in list %s" % (bc_list)}, status=400)

    try:
        ps = ProductionSite.objects.get(id=site)
    except Exception:
        return JsonResponse({"status": "error", "message": "Unknown Production Site"}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if ps.producer not in rights:
        return JsonResponse(
            {"status": "forbidden", "message": "User not allowed to edit production site %s" % (site)}, status=403
        )

    try:
        ProductionSiteOutput.objects.filter(production_site=ps).delete()
        for bc in bc_list:
            obj, created = ProductionSiteOutput.objects.update_or_create(production_site=ps, biocarburant=bc)
            if created:
                # remove errors
                impacted_txs = CarbureLot.objects.filter(carbure_production_site=ps, biofuel=bc)
                background_bulk_scoring(impacted_txs)
                background_bulk_sanity_checks(impacted_txs)
                GenericError.objects.filter(lot__in=impacted_txs, error="BC_NOT_CONFIGURED").delete()
    except Exception:
        return JsonResponse(
            {
                "status": "error",
                "message": "Unknown error. Please contact an administrator",
            },
            status=400,
        )

    return JsonResponse({"status": "success"})
