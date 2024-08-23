import traceback

from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.helpers import get_entity_stock, get_stock_with_metadata


@check_user_rights()
def get_stocks(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    try:
        stock = get_entity_stock(entity_id)
        return get_stock_with_metadata(stock, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get stock"}, status=400
        )
