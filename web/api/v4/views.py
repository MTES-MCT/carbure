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


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def add_comment(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)
    comment = request.POST.get("comment", False)
    if not comment:
        return JsonResponse(
            {"status": "error", "message": "Missing comment"}, status=400
        )
    is_visible_by_admin = request.POST.get("is_visible_by_admin", False)
    is_visible_by_auditor = request.POST.get("is_visible_by_auditor", False)
    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity)

    for lot in lots.iterator():
        if (
            lot.carbure_supplier != entity
            and lot.carbure_client != entity
            and entity.entity_type not in [Entity.AUDITOR, Entity.ADMIN]
        ):
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Entity not authorized to comment on this lot",
                },
                status=403,
            )

        lot_comment = CarbureLotComment()
        lot_comment.entity = entity
        lot_comment.user = request.user
        lot_comment.lot = lot
        if entity.entity_type == Entity.AUDITOR:
            lot_comment.comment_type = CarbureLotComment.AUDITOR
            if is_visible_by_admin == "true":
                lot_comment.is_visible_by_admin = True
        elif entity.entity_type == Entity.ADMIN:
            lot_comment.comment_type = CarbureLotComment.ADMIN
            if is_visible_by_auditor == "true":
                lot_comment.is_visible_by_auditor = True
        else:
            lot_comment.comment_type = CarbureLotComment.REGULAR
        lot_comment.comment = comment
        lot_comment.save()
    return JsonResponse({"status": "success"})


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


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_rfc(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Only the client can accept the lot",
                },
                status=403,
            )

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse(
                {"status": "error", "message": "Cannot accept DRAFT"}, status=400
            )
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse(
                {"status": "error", "message": "Lot already accepted."}, status=400
            )
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {"status": "error", "message": "Lot is Frozen."}, status=400
            )
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse(
                {"status": "error", "message": "Lot is deleted."}, status=400
            )

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.RFC
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
    return JsonResponse({"status": "success"})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_in_stock(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    if entity.entity_type == Entity.OPERATOR:
        return JsonResponse(
            {"status": "error", "message": "Stock unavailable for Operators"},
            status=400,
        )

    for lot in lots.iterator():
        if entity != lot.carbure_client:
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Only the client can accept the lot",
                },
                status=403,
            )

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse(
                {"status": "error", "message": "Cannot accept DRAFT"}, status=400
            )
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse(
                {"status": "error", "message": "Lot already accepted."}, status=400
            )
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {"status": "error", "message": "Lot is Frozen."}, status=400
            )
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse(
                {"status": "error", "message": "Lot is deleted."}, status=400
            )

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.STOCK
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
        stock = CarbureStock()
        stock.parent_lot = lot
        if lot.carbure_delivery_site is None:
            lot.lot_status = CarbureLot.PENDING
            lot.delivery_type = CarbureLot.UNKNOWN
            lot.save()
            return JsonResponse(
                {"status": "error", "message": "Cannot add stock for unknown Depot"},
                status=400,
            )
        stock.depot = lot.carbure_delivery_site
        stock.carbure_client = lot.carbure_client
        stock.remaining_volume = lot.volume
        stock.remaining_weight = lot.weight
        stock.remaining_lhv_amount = lot.lhv_amount
        stock.feedstock = lot.feedstock
        stock.biofuel = lot.biofuel
        stock.country_of_origin = lot.country_of_origin
        stock.carbure_production_site = lot.carbure_production_site
        stock.unknown_production_site = lot.unknown_production_site
        stock.production_country = lot.production_country
        stock.carbure_supplier = lot.carbure_supplier
        stock.unknown_supplier = lot.unknown_supplier
        stock.ghg_reduction = lot.ghg_reduction
        stock.ghg_reduction_red_ii = lot.ghg_reduction_red_ii
        stock.save()
        stock.carbure_id = "%sS%d" % (lot.carbure_id, stock.id)
        stock.save()
    return JsonResponse({"status": "success"})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_blending(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Only the client can accept the lot",
                },
                status=403,
            )

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse(
                {"status": "error", "message": "Cannot accept DRAFT"}, status=400
            )
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse(
                {"status": "error", "message": "Lot already accepted."}, status=400
            )
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {"status": "error", "message": "Lot is Frozen."}, status=400
            )
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse(
                {"status": "error", "message": "Lot is deleted."}, status=400
            )

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.BLENDING
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
    return JsonResponse({"status": "success"})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_export(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Only the client can accept the lot",
                },
                status=403,
            )

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse(
                {"status": "error", "message": "Cannot accept DRAFT"}, status=400
            )
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse(
                {"status": "error", "message": "Lot already accepted."}, status=400
            )
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {"status": "error", "message": "Lot is Frozen."}, status=400
            )
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse(
                {"status": "error", "message": "Lot is deleted."}, status=400
            )

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.EXPORT
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
    return JsonResponse({"status": "success"})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_direct_delivery(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Only the client can accept the lot",
                },
                status=403,
            )

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse(
                {"status": "error", "message": "Cannot accept DRAFT"}, status=400
            )
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse(
                {"status": "error", "message": "Lot already accepted."}, status=400
            )
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {"status": "error", "message": "Lot is Frozen."}, status=400
            )
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse(
                {"status": "error", "message": "Lot is deleted."}, status=400
            )

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.DIRECT
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
    return JsonResponse({"status": "success"})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_processing(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)
    processing_entity_id = request.POST.get("processing_entity_id", False)

    entity = Entity.objects.get(pk=entity_id)
    processing_entity = Entity.objects.get(pk=processing_entity_id)

    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    accepted_lot_ids = []
    processed_lot_ids = []

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Only the client can accept the lot",
                },
                status=403,
            )

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse(
                {"status": "error", "message": "Cannot accept DRAFT"}, status=400
            )
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse(
                {"status": "error", "message": "Lot already accepted."}, status=400
            )
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {"status": "error", "message": "Lot is Frozen."}, status=400
            )
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse(
                {"status": "error", "message": "Lot is deleted."}, status=400
            )

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.PROCESSING
        lot.save()
        accepted_lot_ids.append(lot.id)

        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()

        # create child lot
        parent_lot_id = lot.id
        child_lot = lot
        child_lot.pk = None
        child_lot.carbure_client = processing_entity
        child_lot.delivery_type = CarbureLot.UNKNOWN
        child_lot.lot_status = CarbureLot.PENDING
        child_lot.correction_status = CarbureLot.NO_PROBLEMO
        child_lot.declared_by_supplier = False
        child_lot.declared_by_client = False
        child_lot.added_by = entity
        child_lot.carbure_supplier = entity
        child_lot.unknown_supplier = None
        child_lot.parent_lot_id = parent_lot_id
        child_lot.parent_stock_id = None
        child_lot.save()
        processed_lot_ids.append(child_lot.id)

        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.CREATED
        event.lot = child_lot
        event.user = request.user
        event.save()

    updated_lots = CarbureLot.objects.filter(
        id__in=accepted_lot_ids + processed_lot_ids
    )
    background_bulk_sanity_checks(updated_lots)
    background_bulk_scoring(updated_lots)

    return JsonResponse({"status": "success"})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_trading(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    client_entity_id = request.POST.get("client_entity_id", False)
    unknown_client = request.POST.get("unknown_client", False)
    certificate = request.POST.get("certificate", False)
    status = request.POST.get("status", False)
    entity = Entity.objects.get(id=entity_id)

    if not client_entity_id and not unknown_client:
        return JsonResponse(
            {
                "status": "error",
                "message": "Please specify either client_entity_id or unknown_client",
            },
            status=400,
        )

    if not certificate and entity.default_certificate == "":
        return JsonResponse(
            {"status": "error", "message": "Please specify a certificate"}, status=400
        )

    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    if client_entity_id:
        try:
            client_entity = Entity.objects.get(pk=client_entity_id)
        except:
            return JsonResponse(
                {"status": "error", "message": "Could not find client entity"},
                status=400,
            )
    else:
        client_entity = None

    accepted_lot_ids = []
    transferred_lot_ids = []

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Only the client can accept the lot",
                },
                status=403,
            )

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse(
                {"status": "error", "message": "Cannot accept DRAFT"}, status=400
            )
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse(
                {"status": "error", "message": "Lot already accepted."}, status=400
            )
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {"status": "error", "message": "Lot is Frozen."}, status=400
            )
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse(
                {"status": "error", "message": "Lot is deleted."}, status=400
            )

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.TRADING
        lot.save()
        accepted_lot_ids.append(lot.id)

        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()

        # create child lot
        parent_lot_id = lot.id
        child_lot = lot
        child_lot.pk = None
        child_lot.carbure_client = client_entity
        child_lot.unknown_client = unknown_client
        child_lot.delivery_type = CarbureLot.UNKNOWN
        if child_lot.carbure_client is None:
            # auto-accept when the client is not registered in carbure
            child_lot.lot_status = CarbureLot.ACCEPTED
            child_lot.declared_by_client = True
        else:
            child_lot.declared_by_client = False
            child_lot.lot_status = CarbureLot.PENDING
        child_lot.correction_status = CarbureLot.NO_PROBLEMO
        child_lot.declared_by_supplier = False
        child_lot.added_by = entity
        child_lot.carbure_supplier = entity
        child_lot.supplier_certificate = certificate
        child_lot.unknown_supplier = None
        child_lot.parent_lot_id = parent_lot_id
        child_lot.parent_stock_id = None
        child_lot.save()
        transferred_lot_ids.append(child_lot.id)

        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.CREATED
        event.lot = child_lot
        event.user = request.user
        event.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = child_lot
        event.user = request.user
        event.save()

    updated_lots = CarbureLot.objects.filter(
        id__in=accepted_lot_ids + transferred_lot_ids
    )
    prefetched_data = get_prefetched_data(entity)
    background_bulk_sanity_checks(updated_lots, prefetched_data)
    background_bulk_scoring(updated_lots, prefetched_data)

    return JsonResponse({"status": "success"})


@check_user_rights()
def get_template(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    entity = Entity.objects.get(id=entity_id)
    file_location = template_v4(entity)
    try:
        with open(file_location, "rb") as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type="application/vnd.ms-excel")
            response[
                "Content-Disposition"
            ] = 'attachment; filename="carbure_template.xlsx"'
            return response
    except Exception:
        return JsonResponse(
            {"status": "error", "message": "Error creating template file"}, status=500
        )


@check_user_rights()
def get_template_stock(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    entity = Entity.objects.get(id=entity_id)
    file_location = template_v4_stocks(entity)
    try:
        with open(file_location, "rb") as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type="application/vnd.ms-excel")
            response[
                "Content-Disposition"
            ] = 'attachment; filename="carbure_template_stocks.xlsx"'
            return response
    except Exception:
        return JsonResponse(
            {"status": "error", "message": "Error creating template file"}, status=500
        )


@check_user_rights()
def toggle_warning(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_id = request.POST.get("lot_id")
    errors = request.POST.getlist("errors")
    checked = request.POST.get("checked") == "true"
    try:
        for error in errors:
            try:
                lot = CarbureLot.objects.get(id=lot_id)
                lot_error = GenericError.objects.get(lot_id=lot_id, error=error)
            except:
                traceback.print_exc()
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Could not locate wanted lot or error",
                    },
                    status=404,
                )
            # is creator
            if lot.added_by_id == int(entity_id):
                lot_error.acked_by_creator = checked
            # is recipient
            if lot.carbure_client_id == int(entity_id):
                lot_error.acked_by_recipient = checked
            lot_error.save()
        return JsonResponse({"status": "success"})
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not update warning"}, status=500
        )


@check_user_rights()
def recalc_score(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_id = request.POST.get("lot_id")
    prefetched_data = get_prefetched_data()
    try:
        lot = CarbureLot.objects.get(id=lot_id)
        lot.recalc_reliability_score(prefetched_data)
        lot.save()
    except:
        return ErrorResponse(404)
    return SuccessResponse()


class CancelErrors:
    MISSING_LOT_IDS = "MISSING_LOT_IDS"
    CANCEL_ACCEPT_NOT_ALLOWED = "CANCEL_ACCEPT_NOT_ALLOWED"
    NOT_LOT_CLIENT = "NOT_LOT_CLIENT"
    WRONG_STATUS = "WRONG_STATUS"
    CHILDREN_IN_USE = "CHILDREN_IN_USE"


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def cancel_accept_lots(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_ids = request.POST.getlist("lot_ids", False)
    if not lot_ids:
        return ErrorResponse(400, CancelErrors.MISSING_LOT_IDS)

    entity = Entity.objects.get(pk=entity_id)
    lots = CarbureLot.objects.filter(pk__in=lot_ids)
    for lot in lots.iterator():
        if lot.carbure_client != entity:
            return ErrorResponse(403, CancelErrors.NOT_LOT_CLIENT)

        if lot.lot_status in (
            CarbureLot.DRAFT,
            CarbureLot.PENDING,
            CarbureLot.REJECTED,
            CarbureLot.FROZEN,
            CarbureLot.DELETED,
        ):
            return ErrorResponse(400, CancelErrors.WRONG_STATUS)

        # delete new lots created when the lot was accepted
        if lot.delivery_type in (CarbureLot.PROCESSING, CarbureLot.TRADING):
            children_lots = CarbureLot.objects.filter(parent_lot=lot).exclude(
                lot_status__in=(CarbureLot.DELETED)
            )
            # do not do anything if the children lots are already used
            if (
                children_lots.filter(
                    lot_status__in=(CarbureLot.ACCEPTED, CarbureLot.FROZEN)
                ).count()
                > 0
            ):
                return ErrorResponse(400, CancelErrors.CHILDREN_IN_USE)
            else:
                children_lots.delete()

        # delete new stocks created when the lot was accepted
        if lot.delivery_type == CarbureLot.STOCK:
            children_stocks = CarbureStock.objects.filter(parent_lot=lot)
            children_stocks_children_lots = CarbureLot.objects.filter(
                parent_stock__in=children_stocks
            ).exclude(lot_status=CarbureLot.DELETED)
            children_stocks_children_trans = CarbureStockTransformation.objects.filter(
                source_stock__in=children_stocks
            )
            # do not do anything if the children stocks are already used
            if (
                children_stocks_children_lots.count() > 0
                or children_stocks_children_trans.count() > 0
            ):
                return ErrorResponse(400, CancelErrors.CHILDREN_IN_USE)
            else:
                children_stocks.delete()

        lot.lot_status = CarbureLot.PENDING
        lot.delivery_type = CarbureLot.UNKNOWN
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.CANCELLED
        event.lot = lot
        event.user = request.user
        event.save()
    return SuccessResponse()
