from django.db.models import Q
from django.http import JsonResponse

from core.models import MatierePremiere


def get_feedstocks(request):
    q = request.GET.get("query", False)
    double_count_only = request.GET.get("double_count_only", False)
    mps = MatierePremiere.objects.filter(is_displayed=True).order_by("name")
    if double_count_only == "true":
        mps = mps.filter(is_double_compte=True)
    if q:
        mps = mps.filter(Q(name__icontains=q) | Q(name_en__icontains=q) | Q(code__icontains=q))
    sez = [
        {
            "code": m.code,
            "name": m.name,
            "description": m.description,
            "compatible_alcool": m.compatible_alcool,
            "compatible_graisse": m.compatible_graisse,
            "is_double_compte": m.is_double_compte,
            "category": m.category,
        }
        for m in mps
    ]
    return JsonResponse({"status": "success", "data": sez})
