import sys
import os
import django
import argparse
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *

def pretty_print(tx):
    print('Tx [%d] Lot [%d] Parent Lot [%s] %s %s %d (remaining %d) From %s To %s [Period %s - %s] Forwarded: %s' % (tx.id, tx.lot.id, tx.lot.parent_lot_id, tx.lot.biocarburant.name, tx.lot.matiere_premiere.name, tx.lot.volume, tx.lot.remaining_volume,
                                                                                       tx.lot.carbure_producer.name if tx.lot.carbure_producer else tx.lot.unknown_producer, tx.carbure_client.name if tx.carbure_client else tx.unknown_client,
                                                                                                     tx.lot.period, tx.delivery_date, tx.is_forwarded))

def show_tx_and_parents(tx):
    if tx.parent_tx:
        show_tx_and_parents(tx.parent_tx)
    pretty_print(tx)

def show_tx_and_child(tx):
    pretty_print(tx)
    
    child = LotTransaction.objects.filter(parent_tx=tx)
    if child:
        for c in child:
            show_tx_and_child(c)
        
def show_lot_and_child(id):
    tx = LotTransaction.objects.get(id=id)

    show_tx_and_parents(tx)
    child = LotTransaction.objects.filter(parent_tx=tx)
    for c in child:
        show_tx_and_child(c)
    
if __name__ == '__main__':
    show_lot_and_child(id=int(sys.argv[1]))
