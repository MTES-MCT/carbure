from django.db import transaction
from django.http.response import JsonResponse

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.decorators import check_user_rights
from core.helpers import (
    filter_lots,
    get_entity_lots_by_status,
)
from core.models import (
    CarbureLot,
    CarbureLotEvent,
    Entity,
    UserRights,
)
from transactions.helpers import fill_usage_data, set_trading_delivery_site
from transactions.sanity_checks import get_prefetched_data


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
@transaction.atomic
def accept_direct_delivery(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)
    usage = request.POST.get("usage", "").strip()
    usage_precision = request.POST.get("usage_precision", "").strip()
    unknown_client = request.POST.get("unknown_client", "").strip()
    unknown_delivery_site = request.POST.get("unknown_delivery_site", "").strip()

    if not usage:
        return JsonResponse({"status": "error", "message": "Usage is required for DIRECT"}, status=400)
    if usage not in {value for value, _label in CarbureLot.USAGE_CHOICES}:
        return JsonResponse({"status": "error", "message": "Invalid usage"}, status=400)
    if usage == CarbureLot.USAGE_OTHER and not usage_precision:
        return JsonResponse({"status": "error", "message": "Usage precision is required when usage is OTHER"}, status=400)

    entity = Entity.objects.get(id=entity_id)
    certificate = request.POST.get("certificate", "").strip() or entity.default_certificate
    if not certificate:
        return JsonResponse({"status": "error", "message": "Please specify a certificate"}, status=400)

    lots = get_entity_lots_by_status(entity, status)
    lots = list(filter_lots(lots, request.POST, entity, will_aggregate=True))

    for lot in lots:
        if int(entity_id) != lot.carbure_client_id:
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Only the client can accept the lot",
                },
                status=403,
            )

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

    updated_lot_ids = []
    prefetched_data = get_prefetched_data(entity)
    for lot in lots:
        dispatch_site = lot.carbure_delivery_site or lot.carbure_dispatch_site
        unknown_dispatch_site = lot.unknown_delivery_site or lot.unknown_dispatch_site
        if lot.carbure_delivery_site or (not lot.carbure_dispatch_site and lot.unknown_delivery_site):
            dispatch_country = lot.delivery_site_country
        else:
            dispatch_country = lot.dispatch_site_country

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.TRADING
        set_trading_delivery_site(lot)
        fill_usage_data(lot, {})
        lot.save()
        updated_lot_ids.append(lot.id)
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.entity = entity
        event.save()

        parent_lot_id = lot.id
        lot.pk = None
        lot.parent_lot_id = parent_lot_id
        lot.parent_stock_id = None
        lot.added_by = entity
        lot.carbure_supplier = entity
        lot.unknown_supplier = None
        lot.supplier_certificate = certificate
        lot.supplier_certificate_type = ""
        lot.carbure_vendor = None
        lot.vendor_certificate = None
        lot.vendor_certificate_type = ""
        lot.carbure_client = None
        lot.unknown_client = unknown_client
        lot.carbure_dispatch_site = dispatch_site
        lot.unknown_dispatch_site = None if dispatch_site else unknown_dispatch_site
        lot.dispatch_site_country = dispatch_country
        lot.carbure_delivery_site = None
        lot.unknown_delivery_site = unknown_delivery_site
        lot.delivery_site_country = prefetched_data["countries"]["FR"]
        lot.delivery_type = CarbureLot.DIRECT
        lot.correction_status = CarbureLot.NO_PROBLEMO
        lot.declared_by_supplier = False
        lot.declared_by_client = True
        fill_usage_data(lot, {"usage": usage, "usage_precision": usage_precision})
        lot.save()
        updated_lot_ids.append(lot.id)
        for event_type in (CarbureLotEvent.CREATED, CarbureLotEvent.ACCEPTED):
            CarbureLotEvent.objects.create(lot=lot, event_type=event_type, user=request.user, entity=entity)

    updated_lots = CarbureLot.objects.filter(id__in=updated_lot_ids)
    transaction.on_commit(lambda: background_bulk_sanity_checks(updated_lots, prefetched_data))
    transaction.on_commit(lambda: background_bulk_scoring(updated_lots, prefetched_data))
    return JsonResponse({"status": "success"})
