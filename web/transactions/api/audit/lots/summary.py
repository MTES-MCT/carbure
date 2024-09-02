import traceback

from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.helpers import filter_lots
from core.models import Entity
from transactions.api.admin.helpers import get_admin_summary_data
from transactions.repositories.audit_lots_repository import TransactionsAuditLotsRepository


@check_user_rights(entity_type=[Entity.AUDITOR])
def get_lots_summary(request, entity):
    status = request.GET.get("status", False)
    short = request.GET.get("short", False)
    if not status:
        return JsonResponse({"status": "error", "message": "Missing status"}, status=400)
    try:
        lots = TransactionsAuditLotsRepository.get_auditor_lots_by_status(entity, status, request)
        lots = filter_lots(lots, request.GET, entity, will_aggregate=True)
        summary = get_admin_summary_data(lots, short == "true")
        return JsonResponse({"status": "success", "data": summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": "Could not get lots summary"}, status=400)
