from django.db.models.query_utils import Q
from django.http.response import JsonResponse

from core.decorators import check_admin_rights
from core.models import (
    CarbureLot,
    CarbureStock,
)


@check_admin_rights()
def get_snapshot(request, *args, **kwargs):
    year = request.GET.get("year", False)
    if year:
        try:
            year = int(year)
        except Exception:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Incorrect format for year. Expected YYYY",
                },
                status=400,
            )
    else:
        return JsonResponse({"status": "error", "message": "Missing year"}, status=400)

    lots = CarbureLot.objects.filter(year=year).exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
    stock = CarbureStock.objects.filter(remaining_volume__gt=0)
    alerts = lots.exclude(audit_status=CarbureLot.CONFORM).filter(
        Q(highlighted_by_admin=True) | Q(random_control_requested=True) | Q(ml_control_requested=True)
    )
    data = {}

    data["lots"] = {
        "alerts": alerts.count(),
        "lots": lots.count(),
        "stocks": stock.count(),
    }
    return JsonResponse({"status": "success", "data": data})
