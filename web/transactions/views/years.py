from django.db.models.query_utils import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import CarbureLot, CarbureStockTransformation, Entity
from saf.permissions import HasUserRights


@api_view(["GET"])
@permission_classes(
    [
        IsAuthenticated,
        HasUserRights(None, [Entity.OPERATOR, Entity.PRODUCER, Entity.TRADER]),
    ]
)
def get_years(request, *args, **kwargs):
    entity_id = request.query_params.get("entity_id")
    lots_years = (
        CarbureLot.objects.exclude(lot_status=CarbureLot.DELETED)
        .exclude(Q(lot_status=CarbureLot.DRAFT) & ~Q(added_by_id=entity_id))  # only ignore drafts created by other entities
        .filter(Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id) | Q(added_by_id=entity_id))
        .values_list("year", flat=True)
        .distinct()
    )

    transforms_years = (
        CarbureStockTransformation.objects.select_related("source_stock__parent_lot")
        .exclude(
            source_stock__parent_lot__lot_status__in=[
                CarbureLot.DRAFT,
                CarbureLot.DELETED,
            ]
        )
        .filter(entity_id=entity_id)
        .values_list("transformation_dt__year", flat=True)
        .distinct()
    )

    years = list(set(list(lots_years) + list(transforms_years)))
    return Response(list(years))
