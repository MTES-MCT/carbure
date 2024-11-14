import datetime

from django.http import JsonResponse

from core.decorators import check_user_rights
from core.models import Entity, Pays, UserRights
from transactions.models import EntitySite, ProductionSite


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def add_production_site(request, entity, entity_id):
    country = request.POST.get("country_code")
    name = request.POST.get("name")
    date_mise_en_service = request.POST.get("date_mise_en_service")
    ges_option = request.POST.get("ges_option")
    producer = request.POST.get("entity_id")

    eligible_dc = request.POST.get("eligible_dc")
    eligible_dc = eligible_dc == "true"
    dc_reference = request.POST.get("dc_reference", "")

    site_siret = request.POST.get("site_id")
    address = request.POST.get("address")
    city = request.POST.get("city")
    postal_code = request.POST.get("postal_code")
    manager_name = request.POST.get("manager_name")
    manager_phone = request.POST.get("manager_phone")
    manager_email = request.POST.get("manager_email")

    if country is None:
        return JsonResponse({"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_MISSING_COUNTRY_CODE"}, status=400)
    if name is None:
        return JsonResponse({"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_MISSING_NAME"}, status=400)
    if date_mise_en_service is None:
        return JsonResponse({"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_MISSING_COM_DATE"}, status=400)
    if ges_option is None:
        return JsonResponse({"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_MISSING_GHG_OPTION"}, status=400)
    if site_siret is None:
        return JsonResponse({"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_MISSING_ID"}, status=400)
    if postal_code is None:
        return JsonResponse({"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_MISSING_ZIP_CODE"}, status=400)
    if manager_name is None:
        return JsonResponse({"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_MISSING_MANAGER_NAME"}, status=400)
    if manager_phone is None:
        return JsonResponse({"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_MISSING_MANAGER_PHONE"}, status=400)
    if manager_email is None:
        return JsonResponse({"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_MISSING_MANAGER_EMAIL"}, status=400)
    if city is None:
        return JsonResponse({"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_MISSING_CITY"}, status=400)
    if address is None:
        return JsonResponse({"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_MISSING_ADDRESS"}, status=400)

    try:
        date_mise_en_service = datetime.datetime.strptime(date_mise_en_service, "%Y-%m-%d")
    except Exception:
        return JsonResponse({"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_COM_DATE_WRONG_FORMAT"}, status=400)

    try:
        country = Pays.objects.get(code_pays=country)
    except Exception:
        return JsonResponse(
            {"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_UNKNOWN_COUNTRY_CODE", "extra": country},
            status=400,
        )

    try:
        producer = Entity.objects.get(id=producer, entity_type="Producteur")
    except Exception:
        return JsonResponse(
            {"status": "error", "message": "SETTINGS_ADD_PRODUCTION_SITE_UNKNOWN_PRODUCER", "extra": producer},
            status=400,
        )

    try:
        site = ProductionSite.objects.create(
            created_by=producer,
            country=country,
            name=name,
            city=city,
            address=address,
            postal_code=postal_code,
            eligible_dc=eligible_dc,
            dc_reference=dc_reference,
            site_siret=site_siret,
            manager_name=manager_name,
            manager_phone=manager_phone,
            manager_email=manager_email,
            date_mise_en_service=date_mise_en_service,
            ges_option=ges_option,
            site_type=ProductionSite.PRODUCTION_SITE,
        )

        if site:
            EntitySite.objects.create(entity=producer, site=site)

    except Exception:
        return JsonResponse(
            {
                "status": "error",
                "message": "Unknown error. Please contact an administrator",
            },
            status=400,
        )
    return JsonResponse({"status": "success", "data": site.natural_key()})
