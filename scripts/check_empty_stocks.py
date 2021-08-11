import os
import django
import argparse
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *

empty = LotTransaction.objects.filter(lot__year=2021, lot__remaining_volume=0, lot__status='Validated')
for l in empty:
    child_txs = LotTransaction.objects.filter(lot__parent_lot=l.lot, lot__status='Validated')
    count = child_txs.count()
    if count == 0:
        if l.carbure_client and l.carbure_client.entity_type == Entity.OPERATOR:
            # no doubts here. the remaining volume should be equal to volume
            l.lot.remaining_volume = l.lot.volume
            l.lot.save()
            continue
        else:
            print('requires attention tx id %d' % (l.id))
            if l.lot.biocarburant.code == 'ETH':
                if not l.lot.is_transformed:
                    l.lot.remaining_volume = l.lot.volume
                    l.lot.save()
                    continue
                print(l.lot.biocarburant.code, l.carbure_client, l.unknown_client)
            else:
                l.lot.remaining_volume = l.lot.volume
                l.lot.save()
                continue
    else:
        if count == 1:
            child = child_txs[0]
            if l.lot.biocarburant.code == 'ETH' and child.lot.biocarburant.code == 'ETBE':
                continue
        sum_child = child_txs.filter(is_forwarded=False).aggregate(Sum('lot__volume'))
        sum_volume = sum_child['lot__volume__sum']
        if not sum_volume:
            sum_volume = 0
        if round(sum_volume, 2) != round(l.lot.volume, 2):
            print('Empty lot but child volume != volume: Lot volume [%f] Sum of child [%f]' % (l.lot.volume, sum_volume))
            print('Original Lot Period [%s] Volume [%f] BC [%s] MP [%s] Client [%s]' % (l.lot.period, l.lot.volume, l.lot.biocarburant.code, l.lot.matiere_premiere.code, l.carbure_client.name if l.carbure_client else l.unknown_client))
            for tx in child_txs:
                print('Child txid %d Lot Period [%s] Volume [%f] BC [%s] MP [%s] Client [%s]' % (tx.id, tx.lot.period, tx.lot.volume, tx.lot.biocarburant.code, tx.lot.matiere_premiere.code, tx.carbure_client.name if tx.carbure_client else tx.unknown_client))
                print(tx.natural_key())
