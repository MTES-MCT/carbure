import traceback

from django.http.response import JsonResponse

from core.decorators import check_user_rights, is_auditor
from core.helpers import (
    get_lots_with_metadata,
)

from core.models import (
    Entity,
)
from transactions.repositories.audit_lots_repository import TransactionsAuditLotsRepository


@check_user_rights()
@is_auditor
def get_lots(request, *args, **kwargs):
    status = request.GET.get("status", False)
    selection = request.GET.get("selection", False)
    entity_id = request.GET.get("entity_id", False)
    if not status and not selection:
        return JsonResponse({"status": "error", "message": "Missing status"}, status=400)
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = TransactionsAuditLotsRepository.get_auditor_lots_by_status(entity, status, request)
        return get_lots_with_metadata(lots, entity, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": "Could not get lots"}, status=400)
