from django.db.models import Q
from django.http import JsonResponse

from core.models import Biocarburant


def get_biofuels(request):
    q = request.GET.get("query", False)
    bcs = Biocarburant.objects.filter(is_displayed=True).order_by("name")
    if q:
        bcs = bcs.filter(Q(name__icontains=q) | Q(name_en__icontains=q) | Q(code__icontains=q))
    sez = [
        {
            "code": b.code,
            "name": b.name,
            "description": b.description,
            "pci_kg": b.pci_kg,
            "pci_litre": b.pci_litre,
            "masse_volumique": b.masse_volumique,
            "is_alcool": b.is_alcool,
            "is_graisse": b.is_graisse,
        }
        for b in bcs
    ]
    return JsonResponse({"status": "success", "data": sez})
