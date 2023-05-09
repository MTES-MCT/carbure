from django.http.response import JsonResponse
from django.db.models.query_utils import Q
from core.decorators import check_user_rights

from core.models import (
    CarbureLot,
    CarbureStockTransformation,
)


@check_user_rights()
def get_years(request, *args, **kwargs):
    entity_id = int(kwargs["context"]["entity_id"])
    data_lots = (
        CarbureLot.objects.filter(
            Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id) | Q(added_by_id=entity_id)
        )
        .values_list("year", flat=True)
        .distinct()
    )
    data_transforms = (
        CarbureStockTransformation.objects.filter(entity_id=entity_id)
        .values_list("transformation_dt__year", flat=True)
        .distinct()
    )
    data = set(list(data_transforms) + list(data_lots))
    return JsonResponse({"status": "success", "data": list(data)})
