import json

from django.http import JsonResponse

from core.decorators import check_admin_rights
from doublecount.models import (
    DoubleCountingProduction,
)


@check_admin_rights()
def update_approved_quotas(request):
    approved_quotas = request.POST.get("approved_quotas", False)

    if not approved_quotas:
        return JsonResponse({"status": "error", "message": "Missing approved_quotas POST parameter"}, status=400)
    unpacked = json.loads(approved_quotas)
    for dca_production_id, approved_quota in unpacked:
        try:
            to_update = DoubleCountingProduction.objects.get(id=dca_production_id)
            to_update.approved_quota = approved_quota
            to_update.save()
        except:
            return JsonResponse({"status": "error", "message": "Could not find Production Line"}, status=400)
    return JsonResponse({"status": "success"})
