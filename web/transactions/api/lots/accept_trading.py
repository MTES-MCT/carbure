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
from transactions.sanity_checks.helpers import get_prefetched_data


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
        return JsonResponse({"status": "error", "message": "Please specify a certificate"}, status=400)

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
