from django.http.response import JsonResponse

from core.decorators import check_admin_rights
from core.helpers import (
    get_all_stock,
    get_stock_filters_data,
)
from core.models import ExternalAdminRights


@check_admin_rights(allow_external=[ExternalAdminRights.BIOFUEL])
def get_stock_filters(request, *args, **kwargs):
    field = request.GET.get("field", False)
    if not field:
        return JsonResponse(
            {
                "status": "error",
                "message": "Please specify the field for which you want the filters",
            },
            status=400,
        )
    txs = get_all_stock()
    data = get_stock_filters_data(txs, request.GET, field)
    if data is None:
        return JsonResponse(
            {"status": "error", "message": "Could not find specified filter"},
            status=400,
        )
    else:
        return JsonResponse({"status": "success", "data": data})
