from imp import source_from_cache
import traceback
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import F
from django.db.models import Case, Value, When
from django.db.models.functions.comparison import Coalesce

from django.http.response import JsonResponse
from django.db.models.query_utils import Q
from audit.helpers import get_auditor_lots, get_auditor_lots_by_status

from core.common import SuccessResponse
from core.decorators import check_user_rights, is_auditor
from api.v4.helpers import (
    filter_lots,
    filter_stock,
    get_auditor_stock,
    get_entity_stock,
    get_known_certificates,
    get_lot_comments,
    get_lot_errors,
    get_lot_updates,
    get_lots_with_errors,
    get_lots_with_metadata,
    get_lots_filters_data,
    get_stock_events,
    get_stock_filters_data,
    get_stock_with_metadata,
    get_stocks_summary_data,
)
from api.v4.helpers import get_transaction_distance

from core.models import (
    CarbureLot,
    CarbureLotComment,
    CarbureStock,
    CarbureStockTransformation,
    Entity,
    GenericError,
    UserRights,
)
from core.serializers import (
    CarbureLotAdminSerializer,
    CarbureLotCommentSerializer,
    CarbureLotPublicSerializer,
    CarbureLotReliabilityScoreSerializer,
    CarbureStockPublicSerializer,
    CarbureStockTransformationPublicSerializer,
)
from api.v4.admin import get_admin_summary_data


@check_user_rights()
@is_auditor
def get_stock_details(request, *args, **kwargs):
    stock_id = request.GET.get("stock_id", False)
    if not stock_id:
        return JsonResponse(
            {"status": "error", "message": "Missing stock_id"}, status=400
        )

    stock = CarbureStock.objects.get(pk=stock_id)

    data = {}
    data["stock"] = CarbureStockPublicSerializer(stock).data
    data["parent_lot"] = (
        CarbureLotPublicSerializer(stock.parent_lot).data if stock.parent_lot else None
    )
    data["parent_transformation"] = (
        CarbureStockTransformationPublicSerializer(stock.parent_transformation).data
        if stock.parent_transformation
        else None
    )
    data["children_lot"] = CarbureLotPublicSerializer(
        CarbureLot.objects.filter(parent_stock=stock), many=True
    ).data
    data["children_transformation"] = CarbureStockTransformationPublicSerializer(
        CarbureStockTransformation.objects.filter(source_stock=stock), many=True
    ).data
    data["events"] = get_stock_events(stock.parent_lot)
    data["updates"] = get_lot_updates(stock.parent_lot)
    data["comments"] = get_lot_comments(stock.parent_lot)
    return JsonResponse({"status": "success", "data": data})
