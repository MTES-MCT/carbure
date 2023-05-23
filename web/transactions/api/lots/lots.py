import datetime
import unicodedata
import traceback
from django.db.models.fields import NOT_PROVIDED
from django.db import transaction

from django.http.response import HttpResponse, JsonResponse
from django.db.models.query_utils import Q
from core.common import (
    ErrorResponse,
    SuccessResponse,
    convert_template_row_to_formdata,
    get_uploaded_files_directory,
)
from core.decorators import check_user_rights
from api.v4.helpers import (
    filter_lots,
    get_entity_lots_by_status,
    get_lot_comments,
    get_lot_errors,
    get_lot_updates,
    get_lots_summary_data,
    get_lots_with_metadata,
    get_lots_filters_data,
)
from api.v4.helpers import (
    get_prefetched_data,
    get_transaction_distance,
    get_known_certificates,
)
from api.v4.lots import construct_carbure_lot, bulk_insert_lots
from api.v4.sanity_checks import bulk_scoring
from transactions.sanity_checks import (
    sanity_checks,
    bulk_sanity_checks,
    has_blocking_errors,
)

from core.models import (
    CarbureLot,
    CarbureLotComment,
    CarbureLotEvent,
    CarbureStock,
    CarbureStockEvent,
    CarbureStockTransformation,
    Entity,
    GenericError,
    UserRights,
)
from core.notifications import (
    notify_lots_received,
    notify_lots_rejected,
)
from core.serializers import (
    CarbureLotPublicSerializer,
    CarbureLotReliabilityScoreSerializer,
    CarbureStockPublicSerializer,
)
from core.xlsx_v3 import template_v4, template_v4_stocks
from carbure.tasks import background_bulk_scoring, background_bulk_sanity_checks
from core.traceability import LotNode


@check_user_rights()
def get_lots(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.GET.get("status", False)
    selection = request.GET.get("selection", False)
    export = request.GET.get("export", False)
    if not status and not selection:
        return JsonResponse(
            {"status": "error", "message": "Missing status"}, status=400
        )
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_entity_lots_by_status(entity, status, export)
        return get_lots_with_metadata(lots, entity, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get lots"}, status=400
        )
