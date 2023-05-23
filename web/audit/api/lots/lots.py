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
def get_lots(request, *args, **kwargs):
    status = request.GET.get("status", False)
    selection = request.GET.get("selection", False)
    entity_id = request.GET.get("entity_id", False)
    if not status and not selection:
        return JsonResponse(
            {"status": "error", "message": "Missing status"}, status=400
        )
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_auditor_lots_by_status(entity, status, request)
        return get_lots_with_metadata(lots, entity, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get lots"}, status=400
        )
