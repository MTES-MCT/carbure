from core.decorators import check_user_rights
from core.helpers import get_entity_stock, get_stock_filters_data
from django.http.response import JsonResponse


@check_user_rights()
def get_stock_filters(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    field = request.GET.get("field", False)
    if not field:
        return JsonResponse(
            {
                "status": "error",
                "message": "Please specify the field for which you want the filters",
            },
            status=400,
        )
    txs = get_entity_stock(entity_id)
    data = get_stock_filters_data(txs, request.GET, field)
    if data is None:
        return JsonResponse(
            {"status": "error", "message": "Could not find specified filter"},
            status=400,
        )
    else:
        return JsonResponse({"status": "success", "data": data})
