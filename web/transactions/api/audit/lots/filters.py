from django.http.response import JsonResponse
from core.decorators import check_user_rights
from core.helpers import get_lots_filters_data
from core.models import UserRights
from transactions.repositories.audit_lots_repository import TransactionsAuditLotsRepository


@check_user_rights(role=[UserRights.AUDITOR])
def get_lots_filters(request, entity, entity_id):
    status = request.GET.get("status", False)
    field = request.GET.get("field", False)
    if not field:
        return JsonResponse(
            {
                "status": "error",
                "message": "Please specify the field for which you want the filters",
            },
            status=400,
        )
    lots = TransactionsAuditLotsRepository.get_auditor_lots_by_status(entity, status, request)
    data = get_lots_filters_data(lots, request.GET, entity, field)
    if data is None:
        return JsonResponse(
            {"status": "error", "message": "Could not find specified filter"},
            status=400,
        )
    else:
        return JsonResponse({"status": "success", "data": data})
