from core.decorators import check_user_rights
from django.http.response import JsonResponse
from core.helpers import get_stock_events, get_lot_updates, get_lot_comments
from core.models import CarbureStock, CarbureStock, CarbureStockEvent, UserRights


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def stock_cancel_transformation(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    stock_ids = request.POST.getlist("stock_ids", False)
    if not stock_ids:
        return JsonResponse(
            {"status": "error", "message": "Missing stock_ids"}, status=400
        )

    try:
        stocks = CarbureStock.objects.filter(pk__in=stock_ids)
    except:
        return JsonResponse(
            {"status": "error", "message": "Could not find stock"}, status=400
        )

    for stock in stocks:
        if stock.carbure_client_id != int(entity_id):
            return JsonResponse(
                {"status": "forbidden", "message": "Stock does not belong to you"},
                status=403,
            )

        if stock.parent_transformation_id is None:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Stock does not come from a transformation",
                },
                status=400,
            )

        # all good
        # delete of transformation should trigger a cascading delete of child_lots + recredit volume to the parent_stock
        event = CarbureStockEvent()
        event.stock = stock.parent_transformation.source_stock
        event.event_type = CarbureStockEvent.UNTRANSFORMED
        event.user = request.user
        event.save()
        stock.parent_transformation.delete()
    return JsonResponse({"status": "success"})
