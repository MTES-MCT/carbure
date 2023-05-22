import traceback

from admin.helpers import get_admin_lots_by_status
from api.v4.helpers import (
    filter_lots,
    filter_stock,
    get_all_stock,
    get_known_certificates,
    get_lot_comments,
    get_lot_errors,
    get_lot_updates,
    get_lots_filters_data,
    get_lots_with_metadata,
    get_stock_events,
    get_stock_filters_data,
    get_stock_with_metadata,
    get_stocks_summary_data,
    get_transaction_distance,
)
from core.decorators import is_admin
from core.models import (
    CarbureLot,
    CarbureLotComment,
    CarbureStock,
    CarbureStockTransformation,
    Entity,
    EntityCertificate,
    GenericError,
)
from core.serializers import (
    CarbureLotAdminSerializer,
    CarbureLotCommentSerializer,
    CarbureLotPublicSerializer,
    CarbureLotReliabilityScoreSerializer,
    CarbureStockPublicSerializer,
    CarbureStockTransformationPublicSerializer,
)
from django.db.models import Case, Value, When
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import F
from django.db.models.functions.comparison import Coalesce
from django.db.models.query_utils import Q
from django.http.response import JsonResponse


@is_admin
def get_years(request, *args, **kwargs):
    data_lots = CarbureLot.objects.values_list("year", flat=True).distinct()
    data_transforms = CarbureStockTransformation.objects.values_list(
        "transformation_dt__year", flat=True
    ).distinct()
    data = set(list(data_transforms) + list(data_lots))
    return JsonResponse({"status": "success", "data": list(data)})


@is_admin
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

    lots = CarbureLot.objects.filter(year=year).exclude(
        lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED]
    )
    stock = CarbureStock.objects.filter(remaining_volume__gt=0)
    alerts = lots.filter(
        Q(highlighted_by_admin=True)
        | Q(random_control_requested=True)
        | Q(ml_control_requested=True)
    )
    data = {}

    data["lots"] = {
        "alerts": alerts.count(),
        "lots": lots.count(),
        "stocks": stock.count(),
    }
    return JsonResponse({"status": "success", "data": data})


@is_admin
def get_lots(request, *args, **kwargs):
    status = request.GET.get("status", False)
    selection = request.GET.get("selection", False)
    entity_id = request.GET.get("entity_id", False)
    export = request.GET.get("export", False)
    if not status and not selection:
        return JsonResponse(
            {"status": "error", "message": "Missing status"}, status=400
        )
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_admin_lots_by_status(entity, status, export)
        return get_lots_with_metadata(lots, entity, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get lots"}, status=400
        )


@is_admin
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
        lots = get_admin_lots_by_status(entity, status)
        lots = filter_lots(lots, request.GET, entity, will_aggregate=True)
        summary = get_admin_summary_data(lots, short == "true")
        return JsonResponse({"status": "success", "data": summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get lots summary"}, status=400
        )


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


@is_admin
def get_stocks(request, *args, **kwargs):
    try:
        stock = get_all_stock()
        stock = filter_stock(stock, request.GET)
        return get_stock_with_metadata(stock, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get stock"}, status=400
        )


@is_admin
def get_stocks_summary(request, *args, **kwargs):
    short = request.GET.get("short", False)
    try:
        stock = get_all_stock()
        stock = filter_stock(stock, request.GET)
        summary = get_stocks_summary_data(stock, None, short == "true")
        return JsonResponse({"status": "success", "data": summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not get stock summary"}, status=400
        )


@is_admin
def get_stock_filters(request, *args, **kwargs):
    field = request.GET.get("field", False)
    if not field:
        return JsonResponse(
            {
                "status": "error",
                "message": "Please specify the field for which you want the filters",
            },
            status=400,
        )
    txs = get_all_stock()
    data = get_stock_filters_data(txs, request.GET, field)
    if data is None:
        return JsonResponse(
            {"status": "error", "message": "Could not find specified filter"},
            status=400,
        )
    else:
        return JsonResponse({"status": "success", "data": data})


@is_admin
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


@is_admin
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
    lots = get_admin_lots_by_status(entity, status)
    data = get_lots_filters_data(lots, request.GET, entity, field)
    if data is None:
        return JsonResponse(
            {"status": "error", "message": "Could not find specified filter"},
            status=400,
        )
    else:
        return JsonResponse({"status": "success", "data": data})


@is_admin
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
            lot_error.acked_by_admin = checked
            lot_error.save()
        return JsonResponse({"status": "success"})
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not update warning"}, status=500
        )


@is_admin
def toggle_pin(request, *args, **kwargs):
    selection = request.POST.getlist("selection", [])
    notify_auditor = request.POST.get("notify_auditor") == "true"
    try:
        lots = CarbureLot.objects.filter(id__in=selection)
        lots.update(
            highlighted_by_admin=Case(
                When(highlighted_by_admin=True, then=Value(False)),
                When(highlighted_by_admin=False, then=Value(True)),
            )
        )
        if notify_auditor:
            lots.update(highlighted_by_auditor=True)
        return JsonResponse({"status": "success"})
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not pin lots"}, status=500
        )


@is_admin
def add_comment(request, *args, **kwargs):
    entity_id = request.POST.get("entity_id")
    selection = request.POST.getlist("selection", [])
    comment = request.POST.get("comment", False)
    is_visible_by_auditor = request.POST.get("is_visible_by_auditor") == "true"

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
        lot_comment.comment_type = CarbureLotComment.ADMIN
        lot_comment.is_visible_by_admin = True
        lot_comment.is_visible_by_auditor = is_visible_by_auditor
        lot_comment.comment = comment
        lot_comment.save()

    return JsonResponse({"status": "success"})


def get_admin_summary_data(lots, short=False):
    data = {
        "count": lots.count(),
        "total_volume": lots.aggregate(Sum("volume"))["volume__sum"] or 0,
        "total_weight": lots.aggregate(Sum("weight"))["weight__sum"] or 0,
        "total_lhv_amount": lots.aggregate(Sum("lhv_amount"))["lhv_amount__sum"] or 0,
    }

    if short:
        return data

    pending_filter = Q(lot_status__in=[CarbureLot.PENDING, CarbureLot.REJECTED]) | Q(
        correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED]
    )

    lots = (
        lots.annotate(
            supplier=Coalesce("carbure_supplier__name", "unknown_supplier"),
            client=Coalesce("carbure_client__name", "unknown_client"),
            biofuel_code=F("biofuel__code"),
        )
        .values("supplier", "client", "biofuel_code", "delivery_type")
        .annotate(
            volume_sum=Sum("volume"),
            weight_sum=Sum("weight"),
            lhv_amount_sum=Sum("lhv_amount"),
            avg_ghg_reduction=Sum(F("volume") * F("ghg_reduction_red_ii"))
            / Sum("volume"),
            total=Count("id"),
            pending=Count("id", filter=pending_filter),
        )
        .distinct()
        .order_by()
    )

    data["lots"] = list(lots)
    return data


def get_admin_lot_comments(lot):
    if lot is None:
        return []
    comments = lot.carburelotcomment_set.filter(
        Q(comment_type=CarbureLotComment.ADMIN) | Q(is_visible_by_admin=True)
    )
    return CarbureLotCommentSerializer(comments, many=True).data
