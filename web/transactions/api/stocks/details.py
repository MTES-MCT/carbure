from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.helpers import get_lot_comments, get_lot_updates, get_stock_events
from core.models import CarbureLot, CarbureStock, CarbureStockTransformation
from core.serializers import (
    CarbureLotPublicSerializer,
    CarbureStockPublicSerializer,
    CarbureStockTransformationPublicSerializer,
)


@check_user_rights()
def get_stock_details(request, entity, entity_id):
    stock_id = request.GET.get("stock_id", False)
    if not stock_id:
        return JsonResponse({"status": "error", "message": "Missing stock_id"}, status=400)

    stock = CarbureStock.objects.get(pk=stock_id)
    if stock.carbure_client_id != int(entity_id):
        return JsonResponse({"status": "forbidden", "message": "User not allowed"}, status=403)

    data = {}
    data["stock"] = CarbureStockPublicSerializer(stock).data
    data["parent_lot"] = CarbureLotPublicSerializer(stock.parent_lot).data if stock.parent_lot else None
    data["parent_transformation"] = (
        CarbureStockTransformationPublicSerializer(stock.parent_transformation).data if stock.parent_transformation else None
    )
    children = CarbureLot.objects.filter(parent_stock=stock).exclude(lot_status=CarbureLot.DELETED)
    data["children_lot"] = CarbureLotPublicSerializer(children, many=True).data
    data["children_transformation"] = CarbureStockTransformationPublicSerializer(
        CarbureStockTransformation.objects.filter(source_stock=stock), many=True
    ).data
    data["events"] = get_stock_events(stock.parent_lot)
    data["updates"] = get_lot_updates(stock.parent_lot, entity)
    data["comments"] = get_lot_comments(stock.parent_lot)
    return JsonResponse({"status": "success", "data": data})
