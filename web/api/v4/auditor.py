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
    alerts = lots.filter(
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


@check_user_rights()
@is_auditor
def get_lots_summary(request, *args, **kwargs):
    status = request.GET.get("status", False)
    short = request.GET.get("short", False)
    entity_id = request.GET.get("entity_id", False)
    if not status:
        return JsonResponse(
            {"status": "error", "message": "Missing status"}, status=400
        )
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_auditor_lots_by_status(entity, status, request)
        lots = filter_lots(lots, request.GET, entity, will_aggregate=True)
        summary = get_admin_summary_data(lots, short == "true")
        return JsonResponse({"status": "success", "data": summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get lots summary"}, status=400
        )


@check_user_rights()
@is_auditor
def get_lot_details(request, *args, **kwargs):
    lot_id = request.GET.get("lot_id", False)
    entity_id = request.GET.get("entity_id", False)
    if not lot_id:
        return JsonResponse(
            {"status": "error", "message": "Missing lot_id"}, status=400
        )

    auditor = Entity.objects.get(id=entity_id)
    lot = CarbureLot.objects.get(pk=lot_id)
    client_id = str(lot.carbure_client_id)
    supplier_id = str(lot.carbure_supplier_id)

    has_right_to_audit_client = False
    has_right_to_audit_supplier = False
    if (
        client_id in request.session["rights"]
        and request.session["rights"][client_id] == UserRights.AUDITOR
    ):
        has_right_to_audit_client = True
    if (
        supplier_id in request.session["rights"]
        and request.session["rights"][supplier_id] == UserRights.AUDITOR
    ):
        has_right_to_audit_supplier = True

    if not has_right_to_audit_client and not has_right_to_audit_supplier:
        return JsonResponse(
            {"status": "forbidden", "message": "User not allowed"}, status=403
        )

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
    data["errors"] = get_lot_errors(lot, auditor)
    data["certificates"] = get_known_certificates(lot)
    data["updates"] = get_lot_updates(lot)
    data["comments"] = get_lot_comments(lot)
    data["control_comments"] = get_auditor_lot_comments(lot)
    data["score"] = CarbureLotReliabilityScoreSerializer(
        lot.carburelotreliabilityscore_set.all(), many=True
    ).data
    return JsonResponse({"status": "success", "data": data})


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


@check_user_rights()
@is_auditor
def get_lots_filters(request, *args, **kwargs):
    status = request.GET.get("status", False)
    field = request.GET.get("field", False)
    entity_id = request.GET.get("entity_id", False)
    if not field:
        return JsonResponse(
            {
                "status": "error",
                "message": "Please specify the field for which you want the filters",
            },
            status=400,
        )
    entity = Entity.objects.get(id=entity_id)
    lots = get_auditor_lots_by_status(entity, status, request)
    data = get_lots_filters_data(lots, request.GET, entity, field)
    if data is None:
        return JsonResponse(
            {"status": "error", "message": "Could not find specified filter"},
            status=400,
        )
    else:
        return JsonResponse({"status": "success", "data": data})


@check_user_rights()
@is_auditor
def toggle_warning(request, *args, **kwargs):
    lot_id = request.POST.get("lot_id")
    errors = request.POST.getlist("errors")
    checked = request.POST.get("checked") == "true"
    try:
        for error in errors:
            try:
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
            lot_error.acked_by_auditor = checked
            lot_error.save()
        return JsonResponse({"status": "success"})
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not update warning"}, status=500
        )


@check_user_rights()
@is_auditor
def toggle_pin(request, *args, **kwargs):
    selection = request.POST.getlist("selection", [])
    notify_admin = request.POST.get("notify_admin") == "true"
    try:
        lots = CarbureLot.objects.filter(id__in=selection)
        lots.update(
            highlighted_by_auditor=Case(
                When(highlighted_by_auditor=True, then=Value(False)),
                When(highlighted_by_auditor=False, then=Value(True)),
            )
        )
        if notify_admin:
            lots.update(highlighted_by_admin=True)
        return JsonResponse({"status": "success"})
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not pin lots"}, status=500
        )


@check_user_rights()
@is_auditor
def mark_conform(request, *args, **kwargs):
    selection = request.POST.getlist("selection", [])
    try:
        lots = CarbureLot.objects.filter(id__in=selection)
        lots.update(audit_status=CarbureLot.CONFORM)
        return SuccessResponse()
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not mark lots as conform"}, status=500
        )


@check_user_rights()
@is_auditor
def mark_nonconform(request, *args, **kwargs):
    selection = request.POST.getlist("selection", [])
    try:
        lots = CarbureLot.objects.filter(id__in=selection)
        lots.update(audit_status=CarbureLot.NONCONFORM)
        return SuccessResponse()
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not mark lots as conform"}, status=500
        )


@check_user_rights()
@is_auditor
def add_comment(request, *args, **kwargs):
    entity_id = request.POST.get("entity_id")
    selection = request.POST.getlist("selection", [])
    comment = request.POST.get("comment", False)
    is_visible_by_admin = request.POST.get("is_visible_by_admin") == "true"

    if not comment:
        return JsonResponse(
            {"status": "error", "message": "Missing comment"}, status=400
        )

    entity = Entity.objects.get(id=entity_id)
    lots = CarbureLot.objects.filter(id__in=selection)
    for lot in lots.iterator():
        lot_comment = CarbureLotComment()
        lot_comment.entity = entity
        lot_comment.user = request.user
        lot_comment.lot = lot
        lot_comment.comment_type = CarbureLotComment.AUDITOR
        lot_comment.is_visible_by_auditor = True
        lot_comment.is_visible_by_admin = is_visible_by_admin
        lot_comment.comment = comment
        lot_comment.save()

    return JsonResponse({"status": "success"})


def get_auditor_lots_by_status(entity, status, request):
    lots = get_auditor_lots(request)
    if status == "ALERTS":
        lots = lots.filter(
            Q(highlighted_by_auditor=True)
            | Q(random_control_requested=True)
            | Q(ml_control_requested=True)
        )
    elif status == "LOTS":
        lots = lots.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
    return lots


def get_auditor_lot_comments(lot):
    if lot is None:
        return []
    comments = lot.carburelotcomment_set.filter(
        Q(comment_type=CarbureLotComment.AUDITOR) | Q(is_visible_by_auditor=True)
    )
    return CarbureLotCommentSerializer(comments, many=True).data


@check_user_rights()
@is_auditor
def get_stocks(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    try:
        stock = get_auditor_stock(request.user)
        return get_stock_with_metadata(stock, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get stock"}, status=400
        )


@check_user_rights()
@is_auditor
def get_stocks_summary(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    short = request.GET.get("short", False)
    try:
        stock = get_auditor_stock(request.user)
        stock = filter_stock(stock, request.GET)
        summary = get_stocks_summary_data(stock, None, short == "true")
        return JsonResponse({"status": "success", "data": summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get stock summary"}, status=400
        )


@check_user_rights()
@is_auditor
def get_stock_filters(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    field = request.GET.get("field", False)
    if not field:
        return JsonResponse(
            {
                "status": "error",
                "message": "Please specify the field for which you want the filters",
            },
            status=400,
        )
    txs = get_auditor_stock(request.user)
    data = get_stock_filters_data(txs, request.GET, field)
    if data is None:
        return JsonResponse(
            {"status": "error", "message": "Could not find specified filter"},
            status=400,
        )
    else:
        return JsonResponse({"status": "success", "data": data})


@check_user_rights()
@is_auditor
def get_stock_details(request, *args, **kwargs):
    context = kwargs["context"]
    stock_id = request.GET.get("stock_id", False)
    entity_id = context["entity_id"]
    if not stock_id:
        return JsonResponse(
            {"status": "error", "message": "Missing stock_id"}, status=400
        )

    stock = CarbureStock.objects.get(pk=stock_id)
    client_id = str(stock.carbure_client_id)
    if (
        client_id not in request.session["rights"]
        or request.session["rights"][client_id] != UserRights.AUDITOR
    ):
        return JsonResponse(
            {"status": "forbidden", "message": "User not allowed"}, status=403
        )

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
    children = CarbureLot.objects.filter(parent_stock=stock).exclude(
        lot_status=CarbureLot.DELETED
    )
    data["children_lot"] = CarbureLotPublicSerializer(children, many=True).data
    data["children_transformation"] = CarbureStockTransformationPublicSerializer(
        CarbureStockTransformation.objects.filter(source_stock=stock), many=True
    ).data
    data["events"] = get_stock_events(stock.parent_lot)
    data["updates"] = get_lot_updates(stock.parent_lot)
    data["comments"] = get_lot_comments(stock.parent_lot)
    return JsonResponse({"status": "success", "data": data})
