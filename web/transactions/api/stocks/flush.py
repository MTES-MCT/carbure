from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.models import CarbureLot, CarbureLotEvent, CarbureStock, CarbureStockEvent, UserRights


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def stock_flush(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = int(context["entity_id"])
    stock_ids = request.POST.getlist("stock_ids")
    free_field = request.POST.get("free_field", False)
    if not stock_ids:
        return JsonResponse({"status": "error", "message": "Missing stock_ids"}, status=400)

    for stock_id in stock_ids:
        try:
            stock = CarbureStock.objects.get(pk=stock_id)
        except Exception:
            return JsonResponse({"status": "error", "message": "Could not find stock"}, status=400)

        if stock.carbure_client_id != entity_id:
            return JsonResponse({"status": "forbidden", "message": "Stock does not belong to you"}, status=403)

        volume_to_flush = stock.remaining_volume
        initial_volume = 0
        if stock.parent_lot:
            initial_volume = stock.parent_lot.volume
        elif stock.parent_transformation:
            initial_volume = stock.parent_transformation.volume_destination

        if volume_to_flush > initial_volume * 0.05:
            return JsonResponse(
                {"status": "error", "message": "Cannot flush a stock with a remaining volume greater than 5%"},
                status=400,
            )

        # update remaining stock
        rounded_volume = round(volume_to_flush, 2)
        if rounded_volume >= stock.remaining_volume:
            stock.remaining_volume = 0
            stock.remaining_weight = 0
            stock.remaining_lhv_amount = 0
        else:
            stock.remaining_volume = round(stock.remaining_volume - rounded_volume, 2)
            stock.remaining_weight = stock.get_weight()
            stock.remaining_lhv_amount = stock.get_lhv_amount()
        stock.save()
        # create flushed lot
        lot = stock.get_parent_lot()
        lot.pk = None
        lot.transport_document_type = CarbureLot.OTHER
        lot.transport_document_reference = "N/A - FLUSH"
        lot.volume = rounded_volume
        lot.weight = lot.get_weight()
        lot.lhv_amount = lot.get_lhv_amount()
        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.FLUSHED
        lot.unknown_client = None
        lot.carbure_delivery_site = None
        lot.unknown_delivery_site = None
        lot.delivery_site_country = None
        lot.parent_lot = None
        lot.parent_stock = stock
        if free_field:
            lot.free_field = free_field
        else:
            lot.free_field = "FLUSHED"
        lot.save()
        # create events
        e = CarbureStockEvent()
        e.event_type = CarbureStockEvent.FLUSHED
        e.user = request.user
        e.stock = stock
        e.save()
        e = CarbureLotEvent()
        e.event_type = CarbureLotEvent.CREATED
        e.lot = lot
        e.user = request.user
        e.save()
        e.pk = None
        e.event_type = CarbureLotEvent.ACCEPTED
        e.save()
    return JsonResponse({"status": "success"})
