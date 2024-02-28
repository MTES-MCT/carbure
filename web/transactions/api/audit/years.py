from django.db.models.query_utils import Q
from core.common import SuccessResponse
from core.decorators import check_user_rights
from core.models import CarbureLot, CarbureStockTransformation, Entity
from transactions.repositories.audit_lots_repository import TransactionsAuditLotsRepository


@check_user_rights(entity_type=[Entity.AUDITOR])
def get_years(request):
    audited_entities = TransactionsAuditLotsRepository.get_audited_entities(request.user)

    lots_years = (
        CarbureLot.objects.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        .filter(
            Q(carbure_client__in=audited_entities)
            | Q(carbure_supplier__in=audited_entities)
            | Q(added_by__in=audited_entities)
        )
        .values_list("year", flat=True)
        .distinct()
    )

    transforms_years = (
        CarbureStockTransformation.objects.select_related("source_stock__parent_lot")
        .exclude(source_stock__parent_lot__lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        .filter(entity_id__in=audited_entities)
        .values_list("transformation_dt__year", flat=True)
        .distinct()
    )

    years = list(set(list(lots_years) + list(transforms_years)))
    return SuccessResponse(years)
