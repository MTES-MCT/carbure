import datetime
from django.db.models.aggregates import Count

from django.http.response import JsonResponse
from django.db.models.query_utils import Q
from core.decorators import check_user_rights

from core.models import (
    CarbureLot,
    SustainabilityDeclaration,
)


@check_user_rights()
def get_declarations(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    year = request.GET.get("year", False)
    try:
        year = int(year)
    except Exception:
        return JsonResponse({"status": "error", "message": "Missing year"}, status=400)

    periods = [str(year * 100 + i) for i in range(1, 13)]
    period_dates = [datetime.datetime(year, i, 1) for i in range(1, 13)]

    period_lots = (
        CarbureLot.objects.filter(period__in=periods)
        .filter(Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id))
        .exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        .values("period")
        .annotate(count=Count("id", distinct=True))
    )
    lots_by_period = {}
    for period_lot in period_lots:
        lots_by_period[str(period_lot["period"])] = period_lot["count"]

    pending_period_lots = (
        CarbureLot.objects.filter(period__in=periods)
        .filter(Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id))
        .exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        .filter(
            Q(lot_status__in=[CarbureLot.PENDING, CarbureLot.REJECTED])
            | Q(correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED])
        )
        .values("period")
        .annotate(count=Count("id", distinct=True))
    )
    pending_by_period = {}
    for period_lot in pending_period_lots:
        pending_by_period[str(period_lot["period"])] = period_lot["count"]

    declarations = SustainabilityDeclaration.objects.filter(entity_id=entity_id, period__in=period_dates)
    declarations_by_period = {}
    for declaration in declarations:
        period = declaration.period.strftime("%Y%m")
        declarations_by_period[period] = declaration.natural_key()

    data = []
    for period in periods:
        data.append(
            {
                "period": int(period),
                "lots": lots_by_period[period] if period in lots_by_period else 0,
                "pending": pending_by_period[period] if period in pending_by_period else 0,
                "declaration": declarations_by_period[period] if period in declarations_by_period else None,
            }
        )

    return JsonResponse({"status": "success", "data": data})
