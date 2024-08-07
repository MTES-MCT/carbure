from django.http.response import JsonResponse
from django.db.models.query_utils import Q
from core.decorators import check_user_rights
from core.helpers import get_auditor_stock
from core.models import CarbureLot, Entity
from transactions.repositories.audit_lots_repository import TransactionsAuditLotsRepository


@check_user_rights(entity_type=[Entity.AUDITOR])
def get_snapshot(request):
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

    auditor_lots = TransactionsAuditLotsRepository.get_auditor_lots(request).filter(year=year)
    lots = auditor_lots.filter(year=year).exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
    alerts = lots.exclude(audit_status=CarbureLot.CONFORM).filter(
        Q(highlighted_by_auditor=True) | Q(random_control_requested=True) | Q(ml_control_requested=True)
    )

    auditor_stock = get_auditor_stock(request.user)
    stock = auditor_stock.filter(remaining_volume__gt=0)

    data = {}
    data["lots"] = {
        "alerts": alerts.count(),
        "lots": lots.count(),
        "stocks": stock.count(),
    }
    return JsonResponse({"status": "success", "data": data})
