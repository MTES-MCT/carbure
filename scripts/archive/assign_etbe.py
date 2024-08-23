import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *


def pretty_print_stock(stock):
    print(
        "STOCK {period} [{client}] {id} {carbure_id} {initial_volume} remaining {remaining_volume} {biofuel} {feedstock}".format(
            period=stock.parent_lot.period
            if stock.parent_lot
            else stock.parent_transformation.source_stock.parent_lot.period,
            client=stock.carbure_client.name,
            id=stock.id,
            carbure_id=stock.carbure_id,
            initial_volume=stock.parent_lot.volume if stock.parent_lot else stock.parent_transformation.volume_destination,
            remaining_volume=stock.remaining_volume,
            biofuel=stock.biofuel.name,
            feedstock=stock.feedstock.name,
        )
    )


def pretty_print_lot(lot):
    print(
        "LOT [added by {added_by}] id {id} (parent lot {parent_lot}) (parent_stock {parent_stock}) {carbure_id} {period} {dae} {feedstock} {biofuel} {volume} {delivery_date} {delivery_type} {status} [Supplier {supplier}] [Client {client}]".format(
            added_by=lot.added_by.name,
            id=lot.id,
            parent_lot=lot.parent_lot.id if lot.parent_lot else None,
            parent_stock=lot.parent_stock.id if lot.parent_stock else None,
            carbure_id=lot.carbure_id,
            period=lot.period,
            dae=lot.transport_document_reference,
            biofuel=lot.biofuel.name,
            feedstock=lot.feedstock.name,
            volume=lot.volume,
            delivery_date=lot.delivery_date,
            delivery_type=lot.delivery_type,
            status=lot.lot_status,
            supplier=lot.carbure_supplier.name if lot.carbure_supplier else lot.unknown_supplier,
            client=lot.carbure_client.name if lot.carbure_client else lot.unknown_client,
        )
    )


def pretty_print_transfo(t):
    print("TRANSFORMATION {type} Volume {volume}".format(type=t.transformation_type, volume=t.volume_deducted_from_source))


def recalc():
    print("################################ ETBE ORPHANS")
    odd_lots = CarbureLot.objects.filter(parent_lot__isnull=False, parent_stock__isnull=True, biofuel__code="ETBE")
    for l in odd_lots:
        l.volume = round(l.volume, 2)
        l.save()
        pretty_print_lot(l)
    print("################################ DONE")

    print("################################ ETBE STOCKS")
    odd_lots = CarbureStock.objects.filter(biofuel__code="ETBE", remaining_volume__gt=1)
    for l in odd_lots:
        l.remaining_volume = round(l.remaining_volume, 2)
        l.save()
        pretty_print_stock(l)
    print("################################ DONE")

    odd_lots = CarbureLot.objects.filter(parent_lot__isnull=False, parent_stock__isnull=True, biofuel__code="ETBE")
    for l in odd_lots:
        try:
            stock = CarbureStock.objects.get(remaining_volume=l.volume)
            l.parent_stock = stock
            l.parent_lot = None
            l.save()
            print("Found stock")
        except:
            pass


if __name__ == "__main__":
    recalc()
