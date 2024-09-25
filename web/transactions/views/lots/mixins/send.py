from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.models import CarbureLot, CarbureLotEvent, CarbureStock, Entity
from core.notifications import notify_lots_received
from transactions.sanity_checks import (
    get_prefetched_data,
    has_blocking_errors,
    sanity_checks,
)


class SendMixin:
    @action(methods=["post"], detail=False)
    def send(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)

        filtered_lots = self.filter_queryset(self.get_queryset())
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
                return PermissionDenied({"message": "Entity not authorized to send this lot"})
            if lot.lot_status != CarbureLot.DRAFT:
                return ValidationError({"message": "Lot is not a draft"})

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
                        raise ValidationError(
                            {
                                "message": "Cannot add stock into unknown Depot",
                            }
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
            return Response(
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
                status=status.HTTP_400_BAD_REQUEST,
            )
        sent_lots = CarbureLot.objects.filter(id__in=lot_ids + created_lot_ids)
        background_bulk_sanity_checks(sent_lots, prefetched_data)
        background_bulk_scoring(sent_lots, prefetched_data)
        notify_lots_received(sent_lots)
        return Response(
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
