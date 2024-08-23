
from core.common import SuccessResponse
from core.decorators import check_admin_rights
from core.models import CarbureLot, CarbureStockTransformation


@check_admin_rights()
def get_years(request):
    lots_years = (
        CarbureLot.objects.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        .values_list("year", flat=True)
        .distinct()
    )

    transforms_years = (
        CarbureStockTransformation.objects.select_related("source_stock__parent_lot")
        .exclude(source_stock__parent_lot__lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        .values_list("transformation_dt__year", flat=True)
        .distinct()
    )

    years = list(set(list(lots_years) + list(transforms_years)))
    return SuccessResponse(years)
