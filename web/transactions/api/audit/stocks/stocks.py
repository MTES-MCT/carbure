import traceback
from django.http.response import JsonResponse
from core.decorators import check_user_rights
from core.helpers import get_auditor_stock, get_stock_with_metadata
from core.models import Entity


@check_user_rights(entity_type=[Entity.AUDITOR])
def get_stocks(request):
    try:
        stock = get_auditor_stock(request.user)
        return get_stock_with_metadata(stock, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": "Could not get stock"}, status=400)
