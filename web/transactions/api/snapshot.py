from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.models import (
    CarbureLot,
    CarbureStock,
)


@check_user_rights()
def get_snapshot(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    year = request.GET.get("year", False)
    if year:
        try:
            year = int(year)
        except Exception:
            return JsonResponse({"status": "error", "message": "Incorrect format for year. Expected YYYY"}, status=400)
    else:
        return JsonResponse({"status": "error", "message": "Missing year"}, status=400)

    data = {}
    lots = CarbureLot.objects.filter(year=year)

    drafts = lots.filter(added_by_id=entity_id, lot_status=CarbureLot.DRAFT)
    drafts_imported = drafts.exclude(parent_stock__isnull=False)
    drafts_stocks = drafts.filter(parent_stock__isnull=False)

    lots_in = lots.filter(carbure_client_id=entity_id).exclude(lot_status__in=[CarbureLot.DELETED, CarbureLot.DRAFT])
    lots_in_pending = lots_in.filter(lot_status=CarbureLot.PENDING)
    lots_in_tofix = lots_in.exclude(correction_status=CarbureLot.NO_PROBLEMO)

    stock = CarbureStock.objects.filter(carbure_client_id=entity_id)
    stock_not_empty = stock.filter(remaining_volume__gt=0)

    lots_out = lots.filter(carbure_supplier_id=entity_id).exclude(lot_status__in=[CarbureLot.DELETED, CarbureLot.DRAFT])
    lots_out_pending = lots_out.filter(lot_status=CarbureLot.PENDING)
    lots_out_tofix = lots_out.exclude(correction_status=CarbureLot.NO_PROBLEMO)

    data["lots"] = {
        "draft": drafts.count(),
        "in_total": lots_in.count(),
        "in_pending": lots_in_pending.count(),
        "in_tofix": lots_in_tofix.count(),
        "stock": stock_not_empty.count(),
        "stock_total": stock.count(),
        "out_total": lots_out.count(),
        "out_pending": lots_out_pending.count(),
        "out_tofix": lots_out_tofix.count(),
        "draft_imported": drafts_imported.count(),
        "draft_stocks": drafts_stocks.count(),
    }
    return JsonResponse({"status": "success", "data": data})
