import traceback

from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.helpers import filter_stock, get_entity_stock, get_stocks_summary_data


@check_user_rights()
def get_stocks_summary(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    short = request.GET.get("short", False)
    try:
        stock = get_entity_stock(entity_id)
        stock = filter_stock(stock, request.GET, entity_id)
        summary = get_stocks_summary_data(stock, entity_id, short == "true")
        return JsonResponse({"status": "success", "data": summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get stock summary"}, status=400
        )
