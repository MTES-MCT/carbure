from core.decorators import is_admin
from core.models import (
    CarbureLot,
    CarbureStockTransformation,
)
from django.http.response import JsonResponse


@is_admin
def get_years(request, *args, **kwargs):
    data_lots = CarbureLot.objects.values_list("year", flat=True).distinct()
    data_transforms = CarbureStockTransformation.objects.values_list(
        "transformation_dt__year", flat=True
    ).distinct()
    data = set(list(data_transforms) + list(data_lots))
    return JsonResponse({"status": "success", "data": list(data)})
