import sys
import os
import django
import argparse
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *

def pretty_print(tx):
    print('Tx [%d] Lot [%d] %s %s %d (remaining %d) From %s To %s [Period %s - %s]' % (tx.id, tx.lot.id, tx.lot.biocarburant.name, tx.lot.matiere_premiere.name, tx.lot.volume, tx.lot.remaining_volume,
                                                                                       tx.lot.carbure_producer.name if tx.lot.carbure_producer else tx.lot.unknown_producer, tx.carbure_client.name if tx.carbure_client else tx.unknown_client,
                                                                                       tx.lot.period, tx.delivery_date))

def show_lot_and_child(id):
    tx = LotTransaction.objects.get(id=id)
    pretty_print(tx)
    child = LotTransaction.objects.filter(parent_tx=tx)
    vsum = 0
    for c in child:
        pretty_print(c)
        vsum += c.lot.volume
    print('Child Volume SUM: %d' % (vsum))
    print('Actual Remaining Volume %d' % (tx.lot.remaining_volume))
    print('Theo Remaining Volume %d' % (tx.lot.volume - vsum))    
    print('Diff %d' % (tx.lot.remaining_volume - (tx.lot.volume - vsum)))
    
if __name__ == '__main__':
    show_lot_and_child(id=int(sys.argv[1]))
