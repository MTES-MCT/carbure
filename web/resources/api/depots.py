from django.db.models import Q
from django.http import JsonResponse

from core.models import Depot


def get_depots(request):
    q = request.GET.get("query", False)
    pub = request.GET.get("public_only", False)

    try:
        dsites = Depot.objects.all().order_by("name").filter(is_enabled=True)
        if pub:
            dsites = dsites.filter(private=False)
        if q:
            dsites = dsites.filter(Q(name__icontains=q) | Q(depot_id__icontains=q) | Q(city__icontains=q))
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find delivery sites"}, status=400)

    sez = [d.natural_key() for d in dsites]
    return JsonResponse({"status": "success", "data": sez})
