from django.http.response import JsonResponse
from core.decorators import check_user_rights
from core.helpers import (
    filter_lots,
    get_entity_lots_by_status,
)
from core.helpers import (
    get_prefetched_data,
)
from transactions.sanity_checks import (
    sanity_checks,
    has_blocking_errors,
)

from core.models import (
    CarbureLot,
    CarbureLotEvent,
    CarbureStock,
    Entity,
    UserRights,
)
from core.notifications import (
    notify_lots_received,
)
from carbure.tasks import background_bulk_scoring, background_bulk_sanity_checks


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
                {
                    "status": "forbidden",
                    "message": "Entity not authorized to send this lot",
                },
                status=403,
            )
        if lot.lot_status != CarbureLot.DRAFT:
            return JsonResponse(
                {"status": "error", "message": "Lot is not a draft"}, status=400
            )

        if lot.lot_status in [CarbureLot.ACCEPTED, CarbureLot.FROZEN]:
            # ignore, lot already accepted
            nb_ignored += 1
            continue

        # sanity check !!!
        errors = sanity_checks(lot, prefetched_data)
        if has_blocking_errors(errors):
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
        elif lot.carbure_client == entity and lot.delivery_type not in (
            CarbureLot.UNKNOWN,
            None,
        ):
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
                        {
                            "status": "error",
                            "message": "Cannot add stock into unknown Depot",
                        },
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
