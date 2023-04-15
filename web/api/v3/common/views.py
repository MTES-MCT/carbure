from core.models import Depot, Pays
from django.http import JsonResponse
from django_otp.decorators import otp_required


@otp_required
def create_delivery_site(request):
    name = request.POST.get("name", False)
    city = request.POST.get("city", False)
    country = request.POST.get("country_code", False)
    depot_id = request.POST.get("depot_id", False)
    depot_type = request.POST.get("depot_type", False)

    address = request.POST.get("address", False)
    postal_code = request.POST.get("postal_code", False)

    if not name:
        return JsonResponse({"status": "error", "message": "Missing name"}, status=400)
    if not city:
        return JsonResponse({"status": "error", "message": "Missing city"}, status=400)
    if not country:
        return JsonResponse({"status": "error", "message": "Missing country"}, status=400)
    if not depot_id:
        return JsonResponse({"status": "error", "message": "Missing depot id"}, status=400)
    if not depot_type:
        return JsonResponse({"status": "error", "message": "Missing depot type"}, status=400)
    if not address:
        return JsonResponse({"status": "error", "message": "Missing address"}, status=400)
    if not postal_code:
        return JsonResponse({"status": "error", "message": "Missing postal code"}, status=400)

    try:
        country = Pays.objects.get(code_pays=country)
    except Exception:
        return JsonResponse({"status": "error", "message": "Unknown country_code %s" % (country)}, status=400)

    if depot_type not in [Depot.EFS, Depot.EFPE, Depot.OTHER, Depot.BIOFUELDEPOT, Depot.OILDEPOT]:
        return JsonResponse({"status": "error", "message": "Unknown depot type %s" % (depot_type)}, status=400)

    d = {"name": name, "city": city, "depot_type": depot_type, "address": address, "postal_code": postal_code}

    try:
        Depot.objects.update_or_create(depot_id=depot_id, country=country, defaults=d)
    except Exception:
        return JsonResponse({"status": "error", "message": "Server error"}, status=500)
    return JsonResponse({"status": "success"})
