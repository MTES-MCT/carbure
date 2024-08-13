import traceback
from django.http.response import JsonResponse
from core.decorators import check_user_rights
from core.helpers import filter_stock, get_auditor_stock, get_stocks_summary_data
from core.models import Entity


@check_user_rights(entity_type=[Entity.AUDITOR])
def get_stocks_summary(request):
    short = request.GET.get("short", False)
    try:
        stock = get_auditor_stock(request.user)
        stock = filter_stock(stock, request.GET)
        summary = get_stocks_summary_data(stock, None, short == "true")
        return JsonResponse({"status": "success", "data": summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": "Could not get stock summary"}, status=400)
