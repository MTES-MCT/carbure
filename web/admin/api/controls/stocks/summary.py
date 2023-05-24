import traceback

from core.helpers import (
    filter_stock,
    get_all_stock,
    get_stocks_summary_data,
)
from core.decorators import is_admin
from django.http.response import JsonResponse


@is_admin
def get_stocks_summary(request, *args, **kwargs):
    short = request.GET.get("short", False)
    try:
        stock = get_all_stock()
        stock = filter_stock(stock, request.GET)
        summary = get_stocks_summary_data(stock, None, short == "true")
        return JsonResponse({"status": "success", "data": summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get stock summary"}, status=400
        )
