from core.decorators import check_user_rights
from django.http.response import JsonResponse
from core.helpers import handle_eth_to_etbe_transformation
from core.models import (
    Entity,
    CarbureStock,
    CarbureStock,
    CarbureStockTransformation,
    UserRights,
)
import json


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def stock_transform(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    entity = Entity.objects.get(pk=entity_id)
    payload = request.POST.get("payload", False)
    if not payload:
        return JsonResponse(
            {"status": "error", "message": "Missing payload"}, status=400
        )

    try:
        unserialized = json.loads(payload)
        # expected format: [{stock_id: 12344, transformation_type: 'ETBE', otherfields}]
    except:
        return JsonResponse(
            {"status": "error", "message": "Cannot parse payload into JSON"}, status=400
        )

    if not isinstance(unserialized, list):
        return JsonResponse(
            {"status": "error", "message": "Parsed JSON is not a list"}, status=400
        )

    for entry in unserialized:
        # check minimum fields
        required_fields = ["stock_id", "transformation_type"]
        for field in required_fields:
            if field not in entry:
                return JsonResponse(
                    {"status": "error", "message": "Missing field %s in json object"},
                    status=400,
                )

        try:
            stock = CarbureStock.objects.get(pk=entry["stock_id"])
        except:
            return JsonResponse(
                {"status": "error", "message": "Could not find stock"}, status=400
            )

        if stock.carbure_client != entity:
            return JsonResponse(
                {"status": "forbidden", "message": "Stock does not belong to you"},
                status=403,
            )

        ttype = entry["transformation_type"]
        if ttype == CarbureStockTransformation.ETH_ETBE:
            error = handle_eth_to_etbe_transformation(request.user, stock, entry)
            if error:
                return error
    return JsonResponse({"status": "success"})
