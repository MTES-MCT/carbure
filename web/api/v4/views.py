import datetime
import unicodedata
import dictdiffer
import traceback
from django.db.models.aggregates import Count, Sum
from django.db.models.fields import NOT_PROVIDED
from django.db import transaction

from django.http.response import HttpResponse, JsonResponse
from django.db.models.query_utils import Q
from core.common import ErrorResponse, SuccessResponse, convert_template_row_to_formdata, get_uploaded_files_directory
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
from api.v4.helpers import get_prefetched_data, get_transaction_distance, get_known_certificates
from api.v4.lots import construct_carbure_lot, bulk_insert_lots
from api.v4.sanity_checks import sanity_check, bulk_sanity_checks, bulk_scoring

from core.models import (
    CarbureLot,
    CarbureLotComment,
    CarbureLotEvent,
    CarbureNotification,
    CarbureStock,
    CarbureStockEvent,
    CarbureStockTransformation,
    Entity,
    GenericError,
    SustainabilityDeclaration,
    UserRights,
)
from transactions.helpers import check_locked_year
from core.notifications import (
    notify_correction_done,
    notify_correction_request,
    notify_lots_recalled,
    notify_lots_received,
    notify_lots_rejected,
    notify_lots_recalled,
)
from core.serializers import (
    CarbureLotPublicSerializer,
    CarbureLotReliabilityScoreSerializer,
    CarbureNotificationSerializer,
    CarbureStockPublicSerializer,
)
from core.xlsx_v3 import template_v4, template_v4_stocks
from carbure.tasks import background_bulk_scoring, background_bulk_sanity_checks
from core.carburetypes import CarbureError


@check_user_rights()
def get_years(request, *args, **kwargs):
    entity_id = int(kwargs["context"]["entity_id"])
    data_lots = (
        CarbureLot.objects.filter(
            Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id) | Q(added_by_id=entity_id)
        )
        .values_list("year", flat=True)
        .distinct()
    )
    data_transforms = (
        CarbureStockTransformation.objects.filter(entity_id=entity_id)
        .values_list("transformation_dt__year", flat=True)
        .distinct()
    )
    data = set(list(data_transforms) + list(data_lots))
    return JsonResponse({"status": "success", "data": list(data)})


@check_user_rights()
def get_snapshot(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    year = request.GET.get("year", False)
    if year:
        try:
            year = int(year)
        except Exception:
            return JsonResponse({"status": "error", "message": "Incorrect format for year. Expected YYYY"}, status=400)
    else:
        return JsonResponse({"status": "error", "message": "Missing year"}, status=400)

    data = {}
    lots = CarbureLot.objects.filter(year=year)

    drafts = lots.filter(added_by_id=entity_id, lot_status=CarbureLot.DRAFT)
    drafts_imported = drafts.exclude(parent_stock__isnull=False)
    drafts_stocks = drafts.filter(parent_stock__isnull=False)

    lots_in = lots.filter(carbure_client_id=entity_id).exclude(lot_status__in=[CarbureLot.DELETED, CarbureLot.DRAFT])
    lots_in_pending = lots_in.filter(lot_status=CarbureLot.PENDING)
    lots_in_tofix = lots_in.exclude(correction_status=CarbureLot.NO_PROBLEMO)

    stock = CarbureStock.objects.filter(carbure_client_id=entity_id)
    stock_not_empty = stock.filter(remaining_volume__gt=0)

    lots_out = lots.filter(carbure_supplier_id=entity_id).exclude(lot_status__in=[CarbureLot.DELETED, CarbureLot.DRAFT])
    lots_out_pending = lots_out.filter(lot_status=CarbureLot.PENDING)
    lots_out_tofix = lots_out.exclude(correction_status=CarbureLot.NO_PROBLEMO)

    data["lots"] = {
        "draft": drafts.count(),
        "in_total": lots_in.count(),
        "in_pending": lots_in_pending.count(),
        "in_tofix": lots_in_tofix.count(),
        "stock": stock_not_empty.count(),
        "stock_total": stock.count(),
        "out_total": lots_out.count(),
        "out_pending": lots_out_pending.count(),
        "out_tofix": lots_out_tofix.count(),
        "draft_imported": drafts_imported.count(),
        "draft_stocks": drafts_stocks.count(),
    }
    return JsonResponse({"status": "success", "data": data})


@check_user_rights()
def get_lots(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.GET.get("status", False)
    selection = request.GET.get("selection", False)
    export = request.GET.get("export", False)
    if not status and not selection:
        return JsonResponse({"status": "error", "message": "Missing status"}, status=400)
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_entity_lots_by_status(entity, status, export)
        return get_lots_with_metadata(lots, entity, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": "Could not get lots"}, status=400)


@check_user_rights()
def get_lots_summary(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.GET.get("status", False)
    short = request.GET.get("short", False) == "true"
    if not status:
        return JsonResponse({"status": "error", "message": "Missing status"}, status=400)
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_entity_lots_by_status(entity, status)
        lots = filter_lots(lots, request.GET, entity, will_aggregate=True)
        summary = get_lots_summary_data(lots, entity, short)
        return JsonResponse({"status": "success", "data": summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": "Could not get lots summary"}, status=400)


@check_user_rights()
def get_lot_details(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = int(context["entity_id"])
    lot_id = request.GET.get("lot_id", False)
    if not lot_id:
        return JsonResponse({"status": "error", "message": "Missing lot_id"}, status=400)

    lot = CarbureLot.objects.get(pk=lot_id)
    if lot.carbure_client_id != entity_id and lot.carbure_supplier_id != entity_id and lot.added_by_id != entity_id:
        return JsonResponse({"status": "forbidden", "message": "User not allowed"}, status=403)

    data = {}
    data["lot"] = CarbureLotPublicSerializer(lot).data
    entity = Entity.objects.get(id=entity_id)
    if entity.entity_type == Entity.ADMIN or (
        lot.added_by == entity or (lot.parent_lot and lot.parent_lot.carbure_client == entity)
    ):
        data["parent_lot"] = CarbureLotPublicSerializer(lot.parent_lot).data if lot.parent_lot else None
        data["parent_stock"] = CarbureStockPublicSerializer(lot.parent_stock).data if lot.parent_stock else None
    else:
        data["parent_lot"] = None
        data["parent_stock"] = None
    children = CarbureLot.objects.filter(parent_lot=lot).exclude(lot_status=CarbureLot.DELETED)
    data["children_lot"] = CarbureLotPublicSerializer(children, many=True).data
    data["children_stock"] = CarbureStockPublicSerializer(CarbureStock.objects.filter(parent_lot=lot), many=True).data
    data["distance"] = get_transaction_distance(lot)
    data["errors"] = get_lot_errors(lot, entity)
    data["certificates"] = get_known_certificates(lot)
    data["updates"] = get_lot_updates(lot, entity)
    data["comments"] = get_lot_comments(lot, entity)
    data["score"] = CarbureLotReliabilityScoreSerializer(lot.carburelotreliabilityscore_set.all(), many=True).data
    return JsonResponse({"status": "success", "data": data})


@check_user_rights()
def get_lots_filters(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.GET.get("status", False)
    field = request.GET.get("field", False)
    if not field:
        return JsonResponse(
            {"status": "error", "message": "Please specify the field for which you want the filters"}, status=400
        )
    entity = Entity.objects.get(id=entity_id)
    txs = get_entity_lots_by_status(entity, status)
    data = get_lots_filters_data(txs, request.GET, entity, field)
    if data is None:
        return JsonResponse({"status": "error", "message": "Could not find specified filter"}, status=400)
    else:
        return JsonResponse({"status": "success", "data": data})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def add_lot(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    entity = Entity.objects.get(pk=entity_id)

    d = get_prefetched_data(entity)
    lot_obj, errors = construct_carbure_lot(d, entity, request.POST.dict())
    if not lot_obj:
        return JsonResponse({"status": "error", "message": "Something went wrong"}, status=400)

    # run sanity checks, insert lot and errors
    lots_created = bulk_insert_lots(entity, [lot_obj], [errors], d)
    if len(lots_created) == 0:
        return JsonResponse({"status": "error", "message": "Something went wrong"}, status=500)
    background_bulk_scoring(lots_created)
    e = CarbureLotEvent()
    e.event_type = CarbureLotEvent.CREATED
    e.lot_id = lots_created[0].id
    e.user = request.user
    e.metadata = {"source": "MANUAL"}
    e.save()

    data = CarbureLotPublicSerializer(e.lot).data
    return JsonResponse({"status": "success", "data": data})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def add_excel(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    entity = Entity.objects.get(pk=entity_id)
    d = get_prefetched_data(entity)

    f = request.FILES.get("file")
    if f is None:
        return JsonResponse({"status": "error", "message": "Missing File"}, status=400)

    # save file
    directory = get_uploaded_files_directory()
    now = datetime.datetime.now()
    filename = "%s_%s.xlsx" % (now.strftime("%Y%m%d.%H%M%S"), entity.name.upper())
    filename = "".join((c for c in unicodedata.normalize("NFD", filename) if unicodedata.category(c) != "Mn"))
    filepath = "%s/%s" % (directory, filename)
    with open(filepath, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    data = convert_template_row_to_formdata(entity, d, filepath)
    nb_total = 0
    nb_valid = 0
    nb_invalid = 0
    lots = []
    lots_errors = []
    with transaction.atomic():
        for row in data:
            lot_obj, errors = construct_carbure_lot(d, entity, row)
            if not lot_obj:
                nb_invalid += 1
            else:
                nb_valid += 1
            nb_total += 1
            lots.append(lot_obj)
            lots_errors.append(errors)
        lots_created = bulk_insert_lots(entity, lots, lots_errors, d)
        if len(lots_created) == 0:
            return JsonResponse({"status": "error", "message": "Something went wrong"}, status=500)
        background_bulk_scoring(lots_created)
        for lot in lots_created:
            e = CarbureLotEvent()
            e.event_type = CarbureLotEvent.CREATED
            e.lot_id = lot.id
            e.user = request.user
            e.metadata = {"source": "EXCEL"}
            e.save()
            if lot.parent_stock:
                event = CarbureStockEvent()
                event.event_type = CarbureStockEvent.SPLIT
                event.stock = lot.parent_stock
                event.user = request.user
                event.metadata = {"message": "Envoi lot.", "volume_to_deduct": lot.volume}
                event.save()
    return JsonResponse({"status": "success", "data": {"lots": nb_total, "valid": nb_valid, "invalid": nb_invalid}})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def update_lot(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_id = request.POST.get("lot_id", None)
    if not lot_id:
        return JsonResponse({"status": "error", "message": "Missing lot_id"}, status=400)
    entity = Entity.objects.get(pk=entity_id)

    try:
        existing_lot = CarbureLot.objects.get(id=lot_id, added_by=entity)
    except:
        return JsonResponse({"status": "error", "message": "Could not find lot"}, status=400)

    previous = CarbureLotPublicSerializer(existing_lot).data
    # prefetch some data
    d = get_prefetched_data(entity)
    updated_lot, errors = construct_carbure_lot(d, entity, request.POST.dict(), existing_lot)
    if not updated_lot:
        return JsonResponse({"status": "error", "message": "Something went wrong"}, status=400)
    # run sanity checks, insert lot and errors

    updated_lot.save()
    for e in errors:
        e.lot = updated_lot
    GenericError.objects.bulk_create(errors, batch_size=100)
    bulk_sanity_checks([updated_lot], d)
    background_bulk_scoring([updated_lot], d)
    data = CarbureLotPublicSerializer(updated_lot).data
    diff = dictdiffer.diff(previous, data)
    added = []
    removed = []
    changed = []
    foreign_key_to_field_mapping = {
        "carbure_production_site": "name",
        "carbure_delivery_site": "depot_id",
        "carbure_client": "name",
        "delivery_site_country": "code_pays",
        "country_of_origin": "code_pays",
        "biofuel": "code",
        "feedstock": "code",
    }
    fields_to_ignore = ["lhv_amount", "weight"]
    for d in diff:
        action, field, data = d
        if field in fields_to_ignore:
            continue
        if action == "change":
            if "." in field:
                s = field.split(".")
                mainfield = s[0]
                subfield = s[1]
                if mainfield in foreign_key_to_field_mapping:
                    subfield_to_record = foreign_key_to_field_mapping[mainfield]
                    if subfield != subfield_to_record:
                        continue
                field = mainfield
            changed.append((field, data[0], data[1]))
        if action == "add":
            if isinstance(data, tuple):
                added.append((field, data))
            if isinstance(data, list):
                if field in foreign_key_to_field_mapping:
                    subfield_to_record = foreign_key_to_field_mapping[field]
                    for subfield, value in data:
                        if subfield != subfield_to_record:
                            continue
                        added.append((field, value))
        if action == "remove":
            if isinstance(data, tuple):
                removed.append((field, data))
            if isinstance(data, list):
                if field in foreign_key_to_field_mapping:
                    subfield_to_record = foreign_key_to_field_mapping[field]
                    for subfield, value in data:
                        if subfield != subfield_to_record:
                            continue
                        removed.append((field, value))
    e = CarbureLotEvent()
    e.event_type = CarbureLotEvent.UPDATED
    e.lot = updated_lot
    e.user = request.user
    e.metadata = {"added": added, "removed": removed, "changed": changed}
    e.save()
    return JsonResponse({"status": "success", "data": data})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def duplicate_lot(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_id = request.POST.get("lot_id", None)
    try:
        lot = CarbureLot.objects.get(id=lot_id)
    except Exception:
        return JsonResponse({"status": "error", "message": "Unknown Lot %s" % (lot_id)}, status=400)

    if lot.added_by_id != int(entity_id):
        return JsonResponse({"status": "forbidden", "message": "User not allowed"}, status=403)

    lot.pk = None
    lot.parent_stock = None
    lot.parent_lot = None
    lot_fields_to_remove = [
        "carbure_id",
        "correction_status",
        "lot_status",
        "delivery_status",
        "declared_by_supplier",
        "declared_by_client",
        "highlighted_by_admin",
        "highlighted_by_auditor",
    ]
    lot_meta_fields = {f.name: f for f in CarbureLot._meta.get_fields()}
    for f in lot_fields_to_remove:
        if f in lot_meta_fields:
            meta_field = lot_meta_fields[f]
            if meta_field.default != NOT_PROVIDED:
                setattr(lot, f, meta_field.default)
            else:
                setattr(lot, f, "")
    lot.save()
    data = get_prefetched_data(Entity.objects.get(id=entity_id))
    bulk_sanity_checks([lot], data)
    bulk_scoring([lot], data)
    return JsonResponse({"status": "success"})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def lots_send(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", None)
    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    filtered_lots = filter_lots(lots, request.POST, entity)
    nb_lots = len(filtered_lots)
    nb_sent = 0
    nb_rejected = 0
    nb_ignored = 0
    nb_auto_accepted = 0
    lot_ids = [lot.id for lot in filtered_lots]
    created_lot_ids = []
    prefetched_data = get_prefetched_data(entity)
    for lot in filtered_lots:
        if lot.added_by != entity:
            return JsonResponse(
                {"status": "forbidden", "message": "Entity not authorized to send this lot"}, status=403
            )
        if lot.lot_status != CarbureLot.DRAFT:
            return JsonResponse({"status": "error", "message": "Lot is not a draft"}, status=400)

        if lot.lot_status in [CarbureLot.ACCEPTED, CarbureLot.FROZEN]:
            # ignore, lot already accepted
            nb_ignored += 1
            continue

        # sanity check !!!
        is_sane, errors = sanity_check(lot, prefetched_data)
        if not is_sane:
            nb_rejected += 1
            continue
        nb_sent += 1
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.VALIDATED
        event.lot = lot
        event.user = request.user
        event.save()

        lot.lot_status = CarbureLot.PENDING
        #### SPECIFIC CASES
        # I AM NEITHER THE PRODUCER NOR THE CLIENT (Trading)
        # create two transactions. unknown producer/supplier -> me and me -> client
        if lot.carbure_supplier != entity and lot.carbure_client != entity:
            # AUTO ACCEPT FIRST TRANSACTION
            final_client = lot.carbure_client
            nb_auto_accepted += 1
            lot.lot_status = CarbureLot.ACCEPTED
            lot.delivery_type = CarbureLot.TRADING
            lot.carbure_client = entity
            lot.save()
            first_lot_id = lot.id
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()
            # SECOND TRANSACTION
            lot.pk = None
            lot.parent_lot_id = first_lot_id
            lot.carbure_client = final_client
            lot.unknown_supplier = ""
            lot.carbure_supplier = lot.carbure_vendor
            lot.supplier_certificate = lot.vendor_certificate
            lot.supplier_certificate_type = lot.vendor_certificate_type
            lot.carbure_vendor = None
            lot.vendor_certificate = None
            lot.vendor_certificate_type = ""
            lot.lot_status = CarbureLot.PENDING
            lot.delivery_type = CarbureLot.UNKNOWN
            lot.save()
            created_lot_ids.append(lot.id)
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()
        elif lot.carbure_client_id is None:
            # RFC or EXPORT
            nb_auto_accepted += 1
            lot.lot_status = CarbureLot.ACCEPTED
            lot.save()
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()
        elif lot.carbure_client == entity and lot.delivery_type not in (CarbureLot.UNKNOWN, None):
            lot.lot_status = CarbureLot.ACCEPTED
            lot.save()
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()
            if lot.delivery_type == CarbureLot.STOCK:
                stock = CarbureStock()
                stock.parent_lot = lot
                if lot.carbure_delivery_site is None:
                    lot.lot_status = CarbureLot.DRAFT
                    lot.save()
                    return JsonResponse(
                        {"status": "error", "message": "Cannot add stock into unknown Depot"}, status=400
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
        else:
            pass
        lot.save()
    if nb_sent == 0:
        return JsonResponse(
            {
                "status": "success",
                "data": {
                    "submitted": nb_lots,
                    "sent": nb_sent,
                    "auto-accepted": nb_auto_accepted,
                    "ignored": nb_ignored,
                    "rejected": nb_rejected,
                },
            },
            status=400,
        )
    sent_lots = CarbureLot.objects.filter(id__in=lot_ids + created_lot_ids)
    background_bulk_sanity_checks(sent_lots, prefetched_data)
    background_bulk_scoring(sent_lots, prefetched_data)
    notify_lots_received(sent_lots)
    return JsonResponse(
        {
            "status": "success",
            "data": {
                "submitted": nb_lots,
                "sent": nb_sent,
                "auto-accepted": nb_auto_accepted,
                "ignored": nb_ignored,
                "rejected": nb_rejected,
            },
        }
    )


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def lots_delete(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", None)
    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    filtered_lots = filter_lots(lots, request.POST, entity)
    if filtered_lots.count() == 0:
        return JsonResponse({"status": "error", "message": "Could not find lots to delete"}, status=400)
    for lot in filtered_lots:
        if lot.added_by != entity:
            return JsonResponse(
                {"status": "forbidden", "message": "Entity not authorized to delete this lot"}, status=403
            )

        if lot.lot_status not in [CarbureLot.DRAFT, CarbureLot.REJECTED] and not (
            lot.lot_status in [CarbureLot.PENDING, CarbureLot.ACCEPTED]
            and lot.correction_status == CarbureLot.IN_CORRECTION
        ):
            # cannot delete lot accepted / frozen or already deleted
            return JsonResponse({"status": "error", "message": "Cannot delete lot"}, status=400)

        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.DELETED
        event.lot = lot
        event.user = request.user
        event.save()
        lot.lot_status = CarbureLot.DELETED
        lot.save()
        if lot.parent_stock is not None:
            stock = CarbureStock.objects.get(id=lot.parent_stock.id)  # force refresh from db
            stock.remaining_volume = round(stock.remaining_volume + lot.volume, 2)
            stock.remaining_weight = stock.get_weight()
            stock.remaining_lhv_amount = stock.get_lhv_amount()
            stock.save()
            # save event
            event = CarbureStockEvent()
            event.event_type = CarbureStockEvent.UNSPLIT
            event.stock = lot.parent_stock
            event.user = None
            event.metadata = {"message": "child lot deleted. recredit volume.", "volume_to_credit": lot.volume}
            event.save()
        if lot.parent_lot:
            if lot.parent_lot.delivery_type in [CarbureLot.PROCESSING, CarbureLot.TRADING]:
                lot.parent_lot.lot_status = CarbureLot.PENDING
                lot.parent_lot.delivery_type = CarbureLot.OTHER
                lot.parent_lot.save()
                # save event
                event = CarbureLotEvent()
                event.event_type = CarbureLotEvent.RECALLED
                event.lot = lot.parent_lot
                event.user = None
                event.metadata = {"message": "child lot deleted. back to inbox."}
                event.save()

    return JsonResponse({"status": "success"})


@check_user_rights()
def get_declarations(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    year = request.GET.get("year", False)
    try:
        year = int(year)
    except Exception:
        return JsonResponse({"status": "error", "message": "Missing year"}, status=400)

    periods = [str(year * 100 + i) for i in range(1, 13)]
    period_dates = [datetime.datetime(year, i, 1) for i in range(1, 13)]

    period_lots = (
        CarbureLot.objects.filter(period__in=periods)
        .filter(Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id))
        .exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        .values("period")
        .annotate(count=Count("id", distinct=True))
    )
    lots_by_period = {}
    for period_lot in period_lots:
        lots_by_period[str(period_lot["period"])] = period_lot["count"]

    pending_period_lots = (
        CarbureLot.objects.filter(period__in=periods)
        .filter(Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id))
        .exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        .filter(
            Q(lot_status__in=[CarbureLot.PENDING, CarbureLot.REJECTED])
            | Q(correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED])
        )
        .values("period")
        .annotate(count=Count("id", distinct=True))
    )
    pending_by_period = {}
    for period_lot in pending_period_lots:
        pending_by_period[str(period_lot["period"])] = period_lot["count"]

    declarations = SustainabilityDeclaration.objects.filter(entity_id=entity_id, period__in=period_dates)
    declarations_by_period = {}
    for declaration in declarations:
        period = declaration.period.strftime("%Y%m")
        declarations_by_period[period] = declaration.natural_key()

    data = []
    for period in periods:
        data.append(
            {
                "period": int(period),
                "lots": lots_by_period[period] if period in lots_by_period else 0,
                "pending": pending_by_period[period] if period in pending_by_period else 0,
                "declaration": declarations_by_period[period] if period in declarations_by_period else None,
            }
        )

    return JsonResponse({"status": "success", "data": data})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def add_comment(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)
    comment = request.POST.get("comment", False)
    if not comment:
        return JsonResponse({"status": "error", "message": "Missing comment"}, status=400)
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
                {"status": "forbidden", "message": "Entity not authorized to comment on this lot"}, status=403
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
def request_fix(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_ids = request.POST.getlist("lot_ids", False)
    if not lot_ids:
        return JsonResponse({"status": "error", "message": "Missing lot_ids"}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    try:
        lots = CarbureLot.objects.filter(pk__in=lot_ids)
    except:
        return JsonResponse({"status": "error", "message": "Could not find lots"}, status=400)
    for lot in lots.iterator():
        if check_locked_year(lot.year):
            return ErrorResponse(400, CarbureError.YEAR_LOCKED)

        if lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {"status": "error", "message": "Lot is already declared, now in read-only mode."}, status=400
            )

        if lot.carbure_client != entity:
            return JsonResponse(
                {"status": "forbidden", "message": "Entity not authorized to change this lot"}, status=403
            )
        lot.correction_status = CarbureLot.IN_CORRECTION
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.FIX_REQUESTED
        event.lot = lot
        event.user = request.user
        event.save()
    notify_correction_request(lots)
    return JsonResponse({"status": "success"})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def mark_as_fixed(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_ids = request.POST.getlist("lot_ids", False)
    if not lot_ids:
        return JsonResponse({"status": "error", "message": "Missing lot_ids"}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    try:
        lots = CarbureLot.objects.filter(pk__in=lot_ids)
    except:
        return JsonResponse({"status": "error", "message": "Could not find lots"}, status=400)
    for lot in lots.iterator():
        if lot.added_by != entity and lot.carbure_supplier != entity and lot.carbure_client != entity:
            return JsonResponse(
                {"status": "forbidden", "message": "Entity not authorized to change this lot"}, status=403
            )

        if lot.lot_status == CarbureLot.REJECTED:
            lot.lot_status = CarbureLot.PENDING
            lot.correction_status = CarbureLot.NO_PROBLEMO
        elif lot.added_by == entity and (lot.carbure_client == entity or lot.carbure_client is None):
            lot.correction_status = CarbureLot.NO_PROBLEMO
        else:
            lot.correction_status = CarbureLot.FIXED
        lot.save()
        child = CarbureLot.objects.filter(parent_lot=lot)
        for c in child:
            c.copy_sustainability_data(lot)
            # also copy transaction detail
            c.volume = lot.volume
            c.weight = lot.weight
            c.lhv_amount = lot.lhv_amount
            c.transport_document_type = lot.transport_document_type
            c.transport_document_reference = lot.transport_document_reference
            c.delivery_date = lot.delivery_date
            c.carbure_delivery_site = lot.carbure_delivery_site
            c.unknown_delivery_site = lot.unknown_delivery_site
            c.delivery_site_country = lot.delivery_site_country
            c.carbure_producer = lot.carbure_producer
            c.unknown_producer = lot.unknown_producer
            c.carbure_production_site = lot.carbure_production_site
            c.unknown_production_site = lot.unknown_production_site
            c.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.MARKED_AS_FIXED
        event.lot = lot
        event.user = request.user
        event.save()
    notify_correction_done(lots)
    return JsonResponse({"status": "success"})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def approve_fix(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_ids = request.POST.getlist("lot_ids", False)
    if not lot_ids:
        return JsonResponse({"status": "error", "message": "Missing lot_ids"}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    for lot_id in lot_ids:
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({"status": "error", "message": "Could not find lot id %d" % (lot_id)}, status=400)

        if lot.carbure_supplier != entity and lot.carbure_client != entity:
            return JsonResponse(
                {"status": "forbidden", "message": "Entity not authorized to change this lot"}, status=403
            )
        lot.correction_status = CarbureLot.NO_PROBLEMO
        lot.save()
        # CASCADING CORRECTIONS
        if lot.delivery_type == CarbureLot.STOCK:
            stocks = CarbureStock.objects.filter(parent_lot=lot)
            children = CarbureLot.objects.filter(parent_stock__in=stocks)
            for c in children:
                c.copy_sustainability_data(lot)
                c.save()
                event = CarbureLotEvent()
                event.event_type = CarbureLotEvent.UPDATED
                event.lot = lot
                event.user = request.user
                event.metadata = {"comment": "Cascading update of sustainability data"}
                event.save()
            transformations = CarbureStockTransformation.objects.filter(source_stock__in=stocks)
            for t in transformations:
                new_stock = t.dest_stock
                child = CarbureLot.objects.filter(parent_stock=new_stock)
                for c in child:
                    c.copy_sustainability_data(lot)
                    c.save()
                    event = CarbureLotEvent()
                    event.event_type = CarbureLotEvent.UPDATED
                    event.lot = lot
                    event.user = request.user
                    event.metadata = {"comment": "Cascading update of sustainability data"}
                    event.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.FIX_ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
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
            return JsonResponse({"status": "forbidden", "message": "Only the client can reject this lot"}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({"status": "error", "message": "Cannot reject DRAFT"}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            return JsonResponse({"status": "error", "message": "Lot is already rejected."}, status=400)
        elif lot.lot_status == CarbureLot.ACCEPTED:
            pass
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {"status": "error", "message": "Lot is Frozen. Cannot reject. Please invalidate declaration first."},
                status=400,
            )
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({"status": "error", "message": "Lot is deleted. Cannot reject"}, status=400)

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
def recall_lot(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    lot_ids = request.POST.getlist("lot_ids", False)
    if not lot_ids:
        return JsonResponse({"status": "error", "message": "Missing lot_ids"}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    try:
        lots = CarbureLot.objects.filter(pk__in=lot_ids)
    except:
        return JsonResponse({"status": "error", "message": "Could not find lots"}, status=400)
    for lot in lots.iterator():
        if check_locked_year(lot.year):
            return ErrorResponse(400, CarbureError.YEAR_LOCKED)

        if lot.carbure_supplier != entity and lot.added_by != entity:
            return JsonResponse({"status": "forbidden", "message": "Only the vendor can recall the lot"}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({"status": "error", "message": "Cannot recall DRAFT"}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            return JsonResponse(
                {"status": "error", "message": "Lot is already rejected. Recall has no effect"}, status=400
            )
        elif lot.lot_status == CarbureLot.ACCEPTED:
            # ok but will send a notification to the client
            notify_client = True
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse(
                {"status": "error", "message": "Lot is Frozen. Cannot recall. Please invalidate declaration first."},
                status=400,
            )
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({"status": "error", "message": "Lot is deleted. Cannot recall"}, status=400)

        lot.correction_status = CarbureLot.IN_CORRECTION
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.RECALLED
        event.lot = lot
        event.user = request.user
        event.save()
    notify_lots_recalled(lots)
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
            return JsonResponse({"status": "forbidden", "message": "Only the client can accept the lot"}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({"status": "error", "message": "Cannot accept DRAFT"}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({"status": "error", "message": "Lot already accepted."}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({"status": "error", "message": "Lot is Frozen."}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({"status": "error", "message": "Lot is deleted."}, status=400)

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
        return JsonResponse({"status": "error", "message": "Stock unavailable for Operators"}, status=400)

    for lot in lots.iterator():
        if entity != lot.carbure_client:
            return JsonResponse({"status": "forbidden", "message": "Only the client can accept the lot"}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({"status": "error", "message": "Cannot accept DRAFT"}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({"status": "error", "message": "Lot already accepted."}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({"status": "error", "message": "Lot is Frozen."}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({"status": "error", "message": "Lot is deleted."}, status=400)

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
            return JsonResponse({"status": "error", "message": "Cannot add stock for unknown Depot"}, status=400)
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
            return JsonResponse({"status": "forbidden", "message": "Only the client can accept the lot"}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({"status": "error", "message": "Cannot accept DRAFT"}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({"status": "error", "message": "Lot already accepted."}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({"status": "error", "message": "Lot is Frozen."}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({"status": "error", "message": "Lot is deleted."}, status=400)

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
            return JsonResponse({"status": "forbidden", "message": "Only the client can accept the lot"}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({"status": "error", "message": "Cannot accept DRAFT"}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({"status": "error", "message": "Lot already accepted."}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({"status": "error", "message": "Lot is Frozen."}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({"status": "error", "message": "Lot is deleted."}, status=400)

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
            return JsonResponse({"status": "forbidden", "message": "Only the client can accept the lot"}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({"status": "error", "message": "Cannot accept DRAFT"}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({"status": "error", "message": "Lot already accepted."}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({"status": "error", "message": "Lot is Frozen."}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({"status": "error", "message": "Lot is deleted."}, status=400)

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
            return JsonResponse({"status": "forbidden", "message": "Only the client can accept the lot"}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({"status": "error", "message": "Cannot accept DRAFT"}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({"status": "error", "message": "Lot already accepted."}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({"status": "error", "message": "Lot is Frozen."}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({"status": "error", "message": "Lot is deleted."}, status=400)

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

    updated_lots = CarbureLot.objects.filter(id__in=accepted_lot_ids + processed_lot_ids)
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
            {"status": "error", "message": "Please specify either client_entity_id or unknown_client"}, status=400
        )

    if not certificate and entity.default_certificate == "":
        return JsonResponse({"status": "error", "message": "Please specify a certificate"}, status=400)

    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    if client_entity_id:
        try:
            client_entity = Entity.objects.get(pk=client_entity_id)
        except:
            return JsonResponse({"status": "error", "message": "Could not find client entity"}, status=400)
    else:
        client_entity = None

    accepted_lot_ids = []
    transferred_lot_ids = []

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
            return JsonResponse({"status": "forbidden", "message": "Only the client can accept the lot"}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({"status": "error", "message": "Cannot accept DRAFT"}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({"status": "error", "message": "Lot already accepted."}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({"status": "error", "message": "Lot is Frozen."}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({"status": "error", "message": "Lot is deleted."}, status=400)

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

    updated_lots = CarbureLot.objects.filter(id__in=accepted_lot_ids + transferred_lot_ids)
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
            response["Content-Disposition"] = 'attachment; filename="carbure_template.xlsx"'
            return response
    except Exception:
        return JsonResponse({"status": "error", "message": "Error creating template file"}, status=500)


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
            response["Content-Disposition"] = 'attachment; filename="carbure_template_stocks.xlsx"'
            return response
    except Exception:
        return JsonResponse({"status": "error", "message": "Error creating template file"}, status=500)


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
                return JsonResponse({"status": "error", "message": "Could not locate wanted lot or error"}, status=404)
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
        return JsonResponse({"status": "error", "message": "Could not update warning"}, status=500)


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
            children_lots = CarbureLot.objects.filter(parent_lot=lot).exclude(lot_status__in=(CarbureLot.DELETED))
            # do not do anything if the children lots are already used
            if children_lots.filter(lot_status__in=(CarbureLot.ACCEPTED, CarbureLot.FROZEN)).count() > 0:
                return ErrorResponse(400, CancelErrors.CHILDREN_IN_USE)
            else:
                children_lots.delete()

        # delete new stocks created when the lot was accepted
        if lot.delivery_type == CarbureLot.STOCK:
            children_stocks = CarbureStock.objects.filter(parent_lot=lot)
            children_stocks_children_lots = CarbureLot.objects.filter(parent_stock__in=children_stocks).exclude(
                lot_status=CarbureLot.DELETED
            )
            children_stocks_children_trans = CarbureStockTransformation.objects.filter(source_stock__in=children_stocks)
            # do not do anything if the children stocks are already used
            if children_stocks_children_lots.count() > 0 or children_stocks_children_trans.count() > 0:
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
