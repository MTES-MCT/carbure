import os
import django
import argparse
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *

transformations = ETBETransformation.objects.all()
transformed_in = [e.previous_stock_id for e in transformations]

def pretty_print(tx):
    print('Tx [%d] Parent Tx [%s] Lot [%d] Parent Lot [%s] %s %s %d (remaining %d) From %s To %s [Period %s - %s] Forwarded: %s Stock: %s' % (tx.id, tx.parent_tx_id, tx.lot.id, tx.lot.parent_lot_id, tx.lot.biocarburant.name, tx.lot.matiere_premiere.name, tx.lot.volume, tx.lot.remaining_volume,
                                                                                       tx.lot.carbure_producer.name if tx.lot.carbure_producer else tx.lot.unknown_producer, tx.carbure_client.name if tx.carbure_client else tx.unknown_client,
                                                                                                                               tx.lot.period, tx.delivery_date, tx.is_forwarded, tx.is_stock))


def reset_remaining_volume(tx):
    if tx.id in transformed_in:
        if not tx.lot.is_transformed:
            print('ignoring ETBE stock. marking lot as transformed')
            tx.lot.is_transformed = True
            tx.lot.save()
        return

    
    if tx.lot.volume != tx.lot.remaining_volume:
        print('Reset %s remaining volume from %f to %f. Tx id [%d] Lot id [%d] client %s' % (tx.lot.biocarburant.code, tx.lot.remaining_volume, tx.lot.volume, tx.id, tx.lot.id, tx.carbure_client.name if tx.carbure_client else tx.unknown_client))
        tx.lot.remaining_volume = tx.lot.volume
        #tx.lot.save()
        
def handle_complex_stock(tx, child_tx):
    if tx.lot.is_transformed:
        print("ignoring ETBE")
        return
    if tx.id in transformed_in:
        print('ignoring ETBE stock + marking lot as transformed')
        tx.lot.is_transformed = True
        tx.lot.save()
        return

    if tx.id == 160516:
        print('Recalc stock of tx id %d' % (tx.id))

    sum_volume = 0
    for c in child_tx:
        #pretty_print(c)
        if c.is_forwarded:
            continue
        sum_volume += c.lot.volume
    print('Parent volume [%d] remaining [%d] theo remaining [%d] diff [%d] child volume [%d]' % (tx.lot.volume, tx.lot.remaining_volume, tx.lot.volume - sum_volume, tx.lot.remaining_volume - (tx.lot.volume - sum_volume), sum_volume))    
    diff = round(tx.lot.volume - sum_volume, 2) - round(tx.lot.remaining_volume, 2)
    if abs(diff) > 0.1:
        print('Tx id [%d] Lot Id [%d]' % (tx.id, tx.lot.id))
        print('Parent remaining_volume != initial volume - child volume: Lot initial volume [%f] Sum of child [%f] Remaining [%f] Theo Remaining [%f] Diff [%f]' % (tx.lot.volume, sum_volume, tx.lot.remaining_volume, tx.lot.volume - sum_volume, diff))
        print('Original Lot Period [%s] Volume [%f] BC [%s] MP [%s] Client [%s]' % (tx.lot.period, tx.lot.volume, tx.lot.biocarburant.code, tx.lot.matiere_premiere.code, tx.carbure_client.name if tx.carbure_client else tx.unknown_client))
        for c in child_tx:
            print('Child txid %d Lot Period [%s] Volume [%f] BC [%s] MP [%s] Client [%s]' % (c.id, c.lot.period, c.lot.volume, c.lot.biocarburant.code, c.lot.matiere_premiere.code, c.carbure_client.name if c.carbure_client else c.unknown_client))
        print('Readjusting remaining volume to %f' % (tx.lot.volume - sum_volume))
        tx.lot.remaining_volume = tx.lot.volume - sum_volume
        if input('Save?') == 'y':
            print('Saving')
            tx.lot.save()
        print('New remaining volume: [%f]' % (tx.lot.remaining_volume))
            
def fix_other_stock():
    # fix links between sublots and lots
    txs = LotTransaction.objects.filter(lot__parent_lot__isnull=False)
    for tx in txs:
        if tx.parent_tx is None:
            potential_parents = LotTransaction.objects.filter(lot_id=tx.lot.parent_lot.id)
            if potential_parents.count() == 1:
                tx.parent_tx = potential_parents[0]
                tx.save()
                print('Fix link between parent %s and child %s' % (potential_parents[0].id, tx.id))


    
    stocks = LotTransaction.objects.filter(lot__status='Validated', is_stock=True, is_forwarded=False, lot__is_transformed=False)
    for l in stocks:
        child_txs = LotTransaction.objects.filter(parent_tx=l, lot__status='Validated')
        if l.carbure_client and l.carbure_client.entity_type == Entity.OPERATOR:
            print('Client is an operator. Should not happen')
            if child_txs.count() == 0:
                print('No sub tx, unmark as stock')
                print(l.id, l.lot.period, l.lot.volume, l.lot.remaining_volume, l.lot.biocarburant.code, l.lot.matiere_premiere.code, l.carbure_client.name if l.carbure_client else l.unknown_client)
                if l.lot.volume == l.lot.remaining_volume:
                    # mark as blending
                    l.is_stock = False
                    l.save()
            else:
                if child_txs.count() == 1:
                    print('Operator stock with one children')
                    print('should be marked as processing')
                    l.is_forwarded = True
                    l.save()
                else:
                    print('Operator stock with more than one transaction, need investigation')
                    print(l.id, l.lot.id)
                    print(child_txs)
                    assert(False)
            continue
        if child_txs.count() == 0:
            if l.is_mac:
                print('SHOULD NOT HAPPEN. CANNOT DO is_stock + is_mac')
                if l.lot.volume == l.lot.remaining_volume:
                    # mark as blending
                    l.is_stock = False
                    l.save()                
                reset_remaining_volume(l)
            else:
                if not l.lot.is_transformed:
                    reset_remaining_volume(l)
        else:
            handle_complex_stock(l, child_txs)

if __name__ == '__main__':
    fix_other_stock()
