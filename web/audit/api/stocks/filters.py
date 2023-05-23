from django.http.response import JsonResponse

from core.decorators import check_user_rights, is_auditor
from api.v4.helpers import (
    get_auditor_stock,
    get_stock_filters_data,
)


@check_user_rights()
@is_auditor
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
    txs = get_auditor_stock(request.user)
    data = get_stock_filters_data(txs, request.GET, field)
    if data is None:
        return JsonResponse(
            {"status": "error", "message": "Could not find specified filter"},
            status=400,
        )
    else:
        return JsonResponse({"status": "success", "data": data})
