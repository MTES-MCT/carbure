from django.db.models import Q
from django.http import JsonResponse

from core.models import Pays


def get_countries(request):
    q = request.GET.get("query", False)
    countries = Pays.objects.all().order_by("name")
    if q:
        countries = countries.filter(Q(name__icontains=q) | Q(name_en__icontains=q) | Q(code_pays__icontains=q))
    sez = [c.natural_key() for c in countries]
    return JsonResponse({"status": "success", "data": sez})
