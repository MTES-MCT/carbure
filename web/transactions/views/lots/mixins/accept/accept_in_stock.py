from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.models import CarbureLot, CarbureLotEvent, CarbureStock


class AcceptStockError:
    STOCK_CREATION_FAILED = "STOCK_CREATION_FAILED"


class AcceptStockMixin:
    @action(methods=["post"], detail=False, url_path="accept-in-stock")
    def accept_in_stock(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")

        lots = self.filter_queryset(self.get_queryset())
        # TODO: fix, required ?
        selection = request.data.getlist("selection")
        if len(selection) > 0:
            lots = lots.filter(pk__in=selection)

        errors = {}
        updated_lots = []
        created_events = []
        created_stocks = []
        for lot in lots:
            lot_errors = []
            if int(entity_id) != lot.carbure_client_id:
                lot_errors.append("Only the client can accept the lot")
            if lot.lot_status == CarbureLot.DRAFT:
                lot_errors.append("Cannot accept drafts.")
            elif lot.lot_status == CarbureLot.PENDING:
                pass  # ok no problem
            elif lot.lot_status == CarbureLot.REJECTED:
                pass  # the client changed his mind, ok
            elif lot.lot_status == CarbureLot.ACCEPTED:
                lot_errors.append("Lot is already accepted.")
            elif lot.lot_status == CarbureLot.FROZEN:
                lot_errors.append("Lot is frozen.")
            elif lot.lot_status == CarbureLot.DELETED:
                lot_errors.append("Lot is deleted.")

            lot.lot_status = CarbureLot.ACCEPTED
            lot.delivery_type = CarbureLot.STOCK

            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user

            if lot.carbure_delivery_site is None:
                lot.lot_status = CarbureLot.PENDING
                lot.delivery_type = CarbureLot.UNKNOWN
                lot_errors.append("Cannot add stock for unknown Depot")

            stock = CarbureStock()
            stock.parent_lot = lot
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

            if len(lot_errors) > 0:
                errors[lot.id] = lot_errors
            else:
                updated_lots.append(lot)
                created_events.append(event)
                created_stocks.append(stock)

        if errors:
            raise ValidationError({"message": AcceptStockError.STOCK_CREATION_FAILED, "errors": errors})

        with transaction.atomic():
            CarbureLot.objects.bulk_update(updated_lots, ["lot_status", "delivery_type"])
            CarbureLotEvent.objects.bulk_create(created_events)
            self.bulk_create_stocks(created_stocks)

        return Response({"status": "success"})

    @transaction.atomic()
    def bulk_create_stocks(self, stocks):
        # create the stock rows, then generate carbure_id for all of them
        CarbureStock.objects.bulk_create(stocks)
        new_stocks = CarbureStock.objects.order_by("-id")[0 : len(stocks)]
        [stock.generate_carbure_id() for stock in new_stocks]
        CarbureStock.objects.bulk_update(new_stocks, ["carbure_id"])
        return new_stocks
