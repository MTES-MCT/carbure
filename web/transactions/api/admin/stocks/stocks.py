import traceback

from core.helpers import (
    filter_stock,
    get_all_stock,
    get_stock_with_metadata,
)
from core.decorators import check_admin_rights
from django.http.response import JsonResponse


@check_admin_rights()
def get_stocks(request, *args, **kwargs):
    try:
        stock = get_all_stock()
        stock = filter_stock(stock, request.GET)
        return get_stock_with_metadata(stock, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": "Could not get stock"}, status=400)
