from imp import source_from_cache
import traceback
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import F
from django.db.models import Case, Value, When
from django.db.models.functions.comparison import Coalesce

from django.http.response import JsonResponse
from django.db.models.query_utils import Q
from audit.helpers import get_auditor_lots

from core.common import SuccessResponse
from core.decorators import check_user_rights, is_auditor
from core.helpers import (
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
from core.helpers import get_transaction_distance

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


@check_user_rights()
@is_auditor
def get_snapshot(request, *args, **kwargs):
    year = request.GET.get("year", False)
    if year:
        try:
            year = int(year)
        except Exception:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Incorrect format for year. Expected YYYY",
                },
                status=400,
            )
    else:
        return JsonResponse({"status": "error", "message": "Missing year"}, status=400)

    auditor_lots = get_auditor_lots(request).filter(year=year)
    lots = auditor_lots.filter(year=year).exclude(
        lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED]
    )
    alerts = lots.exclude(audit_status=CarbureLot.CONFORM).filter(
        Q(highlighted_by_auditor=True)
        | Q(random_control_requested=True)
        | Q(ml_control_requested=True)
    )

    auditor_stock = get_auditor_stock(request.user)
    stock = auditor_stock.filter(remaining_volume__gt=0)

    data = {}
    data["lots"] = {
        "alerts": alerts.count(),
        "lots": lots.count(),
        "stocks": stock.count(),
    }
    return JsonResponse({"status": "success", "data": data})
