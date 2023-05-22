from django.http.response import JsonResponse
from audit.helpers import get_auditor_lots
from core.decorators import check_user_rights, is_auditor

from core.models import (
    CarbureStockTransformation,
)


@check_user_rights()
@is_auditor
def get_years(request, *args, **kwargs):
    data_lots = get_auditor_lots(request).values_list("year", flat=True).distinct()
    data_transforms = CarbureStockTransformation.objects.values_list(
        "transformation_dt__year", flat=True
    ).distinct()
    data = set(list(data_transforms) + list(data_lots))
    return JsonResponse({"status": "success", "data": list(data)})
