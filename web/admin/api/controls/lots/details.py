from admin.api.controls.helpers import get_admin_lot_comments
from api.v4.helpers import (
    get_known_certificates,
    get_lot_comments,
    get_lot_errors,
    get_lot_updates,
    get_transaction_distance,
)
from core.decorators import is_admin
from core.models import (
    CarbureLot,
    CarbureStock,
    Entity,
)
from core.serializers import (
    CarbureLotAdminSerializer,
    CarbureLotReliabilityScoreSerializer,
    CarbureStockPublicSerializer,
)
from django.http.response import JsonResponse


@is_admin
def get_lot_details(request, *args, **kwargs):
    lot_id = request.GET.get("lot_id", False)
    entity_id = request.GET.get("entity_id", False)
    if not lot_id:
        return JsonResponse(
            {"status": "error", "message": "Missing lot_id"}, status=400
        )

    entity = Entity.objects.get(id=entity_id)
    lot = CarbureLot.objects.get(pk=lot_id)

    data = {}
    data["lot"] = CarbureLotAdminSerializer(lot).data
    data["parent_lot"] = (
        CarbureLotAdminSerializer(lot.parent_lot).data if lot.parent_lot else None
    )
    data["parent_stock"] = (
        CarbureStockPublicSerializer(lot.parent_stock).data
        if lot.parent_stock
        else None
    )
    data["children_lot"] = CarbureLotAdminSerializer(
        CarbureLot.objects.filter(parent_lot=lot), many=True
    ).data
    data["children_stock"] = CarbureStockPublicSerializer(
        CarbureStock.objects.filter(parent_lot=lot), many=True
    ).data
    data["distance"] = get_transaction_distance(lot)
    data["errors"] = get_lot_errors(lot, entity)
    data["certificates"] = get_known_certificates(lot)
    data["updates"] = get_lot_updates(lot)
    data["comments"] = get_lot_comments(lot)
    data["control_comments"] = get_admin_lot_comments(lot)
    data["score"] = CarbureLotReliabilityScoreSerializer(
        lot.carburelotreliabilityscore_set.all(), many=True
    ).data
    return JsonResponse({"status": "success", "data": data})
