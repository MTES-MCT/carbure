from django.http import JsonResponse

from core.decorators import check_user_rights
from core.models import Pays, UserRights
from transactions.models import ProductionSite


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def update_production_site(request, entity, entity_id):
    production_site_id = request.POST.get("production_site_id", False)

    if not production_site_id:
        return JsonResponse({"status": "error", "message": "Missing field production_site_id"}, status=400)

    psite = ProductionSite.objects.get(id=production_site_id, created_by=entity)

    country_code = request.POST.get("country_code")
    name = request.POST.get("name")
    date_mise_en_service = request.POST.get("date_mise_en_service")
    ges_option = request.POST.get("ges_option")

    eligible_dc = request.POST.get("eligible_dc")
    eligible_dc = eligible_dc == "true"
    dc_reference = request.POST.get("dc_reference")

    site_siret = request.POST.get("site_id")
    city = request.POST.get("city")
    address = request.POST.get("address")
    postal_code = request.POST.get("postal_code")
    manager_name = request.POST.get("manager_name")
    manager_phone = request.POST.get("manager_phone")
    manager_email = request.POST.get("manager_email")

    if name:
        psite.name = name
    if ges_option:
        psite.ges_option = ges_option
    if date_mise_en_service:
        psite.date_mise_en_service = date_mise_en_service
    if eligible_dc is not None:
        psite.eligible_dc = eligible_dc
    if dc_reference:
        psite.dc_reference = dc_reference
    if site_siret:
        psite.site_siret = site_siret
    if city:
        psite.city = city
    if address:
        psite.address = address
    if postal_code:
        psite.postal_code = postal_code
    if manager_name:
        psite.manager_name = manager_name
    if manager_phone:
        psite.manager_phone = manager_phone
    if manager_email:
        psite.manager_email = manager_email
    if country_code:
        try:
            country = Pays.objects.get(code_pays=country_code)
            psite.country = country
        except Exception:
            return JsonResponse({"status": "error", "message": "Unknown country"}, status=400)

    psite.save()
    return JsonResponse({"status": "success"})
