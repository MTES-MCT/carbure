from django.http import JsonResponse

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.decorators import check_user_rights
from core.models import CarbureLot, GenericError, MatierePremiere, UserRights
from producers.models import ProductionSiteInput
from transactions.models import Site as ProductionSite


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def set_production_site_feedstocks(request, entity, entity_id):
    site = request.POST.get("production_site_id")
    mp_list = request.POST.getlist("matiere_premiere_codes")

    if site is None:
        return JsonResponse({"status": "error", "message": "Missing production_site_id"}, status=400)
    if mp_list is None:
        return JsonResponse({"status": "error", "message": "Missing matiere_premiere_codes"}, status=400)

    try:
        mp_list = MatierePremiere.objects.filter(code__in=mp_list)
    except Exception:
        return JsonResponse({"status": "error", "message": "Unknown MP in list %s" % (mp_list)}, status=400)

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
        ProductionSiteInput.objects.filter(production_site=ps).delete()
        for mp in mp_list:
            obj, created = ProductionSiteInput.objects.update_or_create(production_site=ps, matiere_premiere=mp)
            if created:
                # remove errors
                impacted_txs = CarbureLot.objects.filter(carbure_production_site=ps, feedstock=mp)
                background_bulk_scoring(impacted_txs)
                background_bulk_sanity_checks(impacted_txs)
                GenericError.objects.filter(lot__in=impacted_txs, error="MP_NOT_CONFIGURED").delete()
    except Exception:
        return JsonResponse(
            {
                "status": "error",
                "message": "Unknown error. Please contact an administrator",
            },
            status=400,
        )
    return JsonResponse({"status": "success"})
