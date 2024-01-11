from django.db.models.query_utils import Q
from core.common import SuccessResponse
from core.decorators import check_user_rights
from core.models import CarbureLot, CarbureStockTransformation


@check_user_rights()
def get_years(request, entity_id):
    lots_years = (
        CarbureLot.objects.exclude(lot_status=CarbureLot.DELETED)
        .exclude(Q(lot_status=CarbureLot.DRAFT) & ~Q(added_by_id=entity_id))  # only ignore drafts created by other entities
        .filter(Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id) | Q(added_by_id=entity_id))
        .values_list("year", flat=True)
        .distinct()
    )

    transforms_years = (
        CarbureStockTransformation.objects.select_related("source_stock__parent_lot")
        .exclude(source_stock__parent_lot__lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        .filter(entity_id=entity_id)
        .values_list("transformation_dt__year", flat=True)
        .distinct()
    )

    years = list(set(list(lots_years) + list(transforms_years)))
    return SuccessResponse(list(years))
