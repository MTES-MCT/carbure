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
from core.helpers import (
    filter_lots,
    get_entity_lots_by_status,
    get_lot_comments,
    get_lot_errors,
    get_lot_updates,
    get_lots_summary_data,
    get_lots_with_metadata,
    get_lots_filters_data,
)
from core.helpers import (
    get_prefetched_data,
    get_transaction_distance,
    get_known_certificates,
)
from transactions.helpers import construct_carbure_lot, bulk_insert_lots
from transactions.sanity_checks.sanity_checks import bulk_scoring
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


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def reject_lot(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots.iterator():
        if lot.carbure_client != entity:
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Only the client can reject this lot",
                },
                status=403,
            )

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse(
                {"status": "error", "message": "Cannot reject DRAFT"}, status=400
            )
        elif lot.lot_status == CarbureLot.PENDING:
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            return JsonResponse(
                {"status": "error", "message": "Lot is already rejected."}, status=400
            )
        elif lot.lot_status == CarbureLot.ACCEPTED:
            pass
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Lot is Frozen. Cannot reject. Please invalidate declaration first.",
                },
                status=400,
            )
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse(
                {"status": "error", "message": "Lot is deleted. Cannot reject"},
                status=400,
            )

        lot.lot_status = CarbureLot.REJECTED
        lot.correction_status = CarbureLot.IN_CORRECTION
        lot.carbure_client = None
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.REJECTED
        event.lot = lot
        event.user = request.user
        event.save()
    notify_lots_rejected(lots)
    return JsonResponse({"status": "success"})
