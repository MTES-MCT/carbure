import os

import django
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *


def pretty_print_stock(stock):
    print("STOCK {period} [{client}] {id} {carbure_id} {initial_volume} remaining {remaining_volume} {biofuel} {feedstock}".format(period=stock.parent_lot.period if stock.parent_lot else stock.parent_transformation.source_stock.parent_lot.period, client=stock.carbure_client.name, id=stock.id, carbure_id=stock.carbure_id, initial_volume=stock.parent_lot.volume if stock.parent_lot else stock.parent_transformation.volume_destination, remaining_volume=stock.remaining_volume, biofuel=stock.biofuel.name, feedstock=stock.feedstock.name))

def pretty_print_lot(lot):
    print("LOT [added by {added_by}] id {id} (parent lot {parent_lot}) (parent_stock {parent_stock}) {carbure_id} {period} {dae} {feedstock} {biofuel} {volume} {delivery_date} {delivery_type} {status} [Supplier {supplier}] [Client {client}]".format(added_by=lot.added_by.name, id=lot.id, parent_lot=lot.parent_lot.id if lot.parent_lot else None, parent_stock=lot.parent_stock.id if lot.parent_stock else None, carbure_id=lot.carbure_id, period=lot.period, dae=lot.transport_document_reference, biofuel=lot.biofuel.name, feedstock=lot.feedstock.name, volume=lot.volume, delivery_date=lot.delivery_date, delivery_type=lot.delivery_type, status=lot.lot_status, supplier=lot.carbure_supplier.name if lot.carbure_supplier else lot.unknown_supplier, client=lot.carbure_client.name if lot.carbure_client else lot.unknown_client))

def pretty_print_transfo(t):
    print("TRANSFORMATION {type} Volume {volume}".format(type=t.transformation_type, volume=t.volume_deducted_from_source))

def recalc():
    print('################################ ETBE ORPHANS')
    odd_lots = CarbureLot.objects.filter(parent_lot__isnull=False, parent_stock__isnull=True, biofuel__code='ETBE')
    for l in odd_lots:
        pretty_print_lot(l)
    print('################################ DONE')

    stocks = CarbureStock.objects.all()
    for stock in stocks:
        # find child
        child_volume = CarbureLot.objects.filter(parent_stock=stock).exclude(lot_status=CarbureLot.DELETED).aggregate(child_volume=Sum('volume'))
        vol = child_volume['child_volume']
        if vol is None:
            vol = 0
        transformations_volume = CarbureStockTransformation.objects.filter(source_stock=stock).aggregate(vol=Sum('volume_deducted_from_source'))
        if transformations_volume['vol'] is not None:
            vol += transformations_volume['vol']
        initial_volume = stock.parent_lot.volume if stock.parent_lot else stock.parent_transformation.volume_destination
        theo_remaining = initial_volume - vol
        diff = stock.remaining_volume - theo_remaining
        if abs(diff) > 0.1:
            print('Initial volume [%.2f] Child volume [%.2f] Theo remaining [%.2f] Remaining [%.2f]: Diff [%.2f]' % (initial_volume, vol, theo_remaining, stock.remaining_volume, diff))
            pretty_print_stock(stock)
            child = CarbureLot.objects.filter(parent_stock=stock).exclude(lot_status=CarbureLot.DELETED)
            print('Child lots:')
            for c in child:
                pretty_print_lot(c)
            transformations = CarbureStockTransformation.objects.filter(source_stock=stock)
            print('Child transfos')
            for t in transformations:
                pretty_print_transfo(t)
            adjust = input("press enter to continue")
            if adjust == 'y':
                print('Adjusting volume:')
                stock.remaining_volume = round(theo_remaining, 2)
                stock.remaining_weight = stock.get_weight()
                stock.remaining_lhv_amount = stock.get_lhv_amount()
                stock.save()


if __name__ == '__main__':
    recalc()

