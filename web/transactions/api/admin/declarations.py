from dateutil.relativedelta import relativedelta


import datetime
import math
from django.http.response import JsonResponse

from core.decorators import is_admin

from core.models import Entity, SustainabilityDeclaration, CarbureLot
from core.serializers import (
    SustainabilityDeclarationSerializer,
)


@is_admin
def get_declarations(request):
    period = request.GET.get("period", False)
    if not period:
        return JsonResponse({"status": "error", "message": "Missing period"})

    year = math.floor(int(period) / 100)
    month = int(period) % 100
    period_now_date = datetime.date(year=year, month=month, day=1)
    period_before_date = period_now_date - relativedelta(months=1)
    period_after_date = period_now_date + relativedelta(months=1)
    period_dates = [period_before_date, period_now_date, period_after_date]
    periods = [
        period_before_date.year * 100 + period_before_date.month,
        int(period),
        period_after_date.year * 100 + period_after_date.month,
    ]

    data = []
    lot_counts = get_period_entity_lot_count(periods)
    declaration_query = SustainabilityDeclaration.objects.filter(
        period__in=period_dates, entity__entity_type__in=[Entity.PRODUCER, Entity.OPERATOR, Entity.TRADER]
    ).select_related("entity")
    declarations = SustainabilityDeclarationSerializer(declaration_query, many=True).data
    for decl in declarations:
        entity_id = decl.get("entity").get("id")
        period = decl.get("period")
        count = (
            lot_counts[entity_id][period]
            if entity_id in lot_counts and period in lot_counts[entity_id]
            else {"drafts": 0, "output": 0, "input": 0, "corrections": 0}
        )
        data.append({"declaration": decl, "count": count})

    return JsonResponse({"status": "success", "data": data})


def get_period_entity_lot_count(periods):
    lots = CarbureLot.objects.filter(period__in=periods).values(
        "added_by_id", "carbure_supplier_id", "carbure_client_id", "lot_status", "correction_status", "period"
    )

    declarations = {}

    for lot in lots.iterator():
        period = lot["period"] or None
        author = lot["added_by_id"] or None
        vendor = lot["carbure_supplier_id"] or None
        client = lot["carbure_client_id"] or None

        if author and lot["lot_status"] == CarbureLot.DRAFT:
            declaration = init_declaration(author, period, declarations)
            declaration["drafts"] += 1
        else:
            if client:
                declaration = init_declaration(client, period, declarations)
                declaration["input"] += 1
            if vendor:
                declaration = init_declaration(vendor, period, declarations)
                declaration["output"] += 1
            if author and lot["correction_status"] != CarbureLot.NO_PROBLEMO:
                declaration = init_declaration(author, period, declarations)
                declaration["corrections"] += 1

    return declarations


def init_declaration(entity, period, declarations):
    if entity not in declarations:
        declarations[entity] = {}
    if period not in declarations[entity]:
        declarations[entity][period] = {"drafts": 0, "output": 0, "input": 0, "corrections": 0}
    return declarations[entity][period]
