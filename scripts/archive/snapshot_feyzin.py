import os
import django
import argparse
from django.db.models import Sum, Count, Min, Q
import calendar
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import *
from django.core import serializers
    
def snapshot_feyzin_data():
    feyzin = Entity.objects.get(name='TERF Feyzin')
    terf = Entity.objects.get(name='TERF')
    
    transactions = LotTransaction.objects.filter(Q(carbure_client=feyzin) | Q(carbure_vendor=feyzin))
    serialized_obj = serializers.serialize('json', transactions)
    f = open('transactions.json', 'w')
    f.write(serialized_obj)
    f.close()

    lots_ids = [tx.lot_id for tx in transactions]
    lots = LotV2.objects.filter(id__in=lots_ids)
    serialized_obj = serializers.serialize('json', lots)
    f = open('lots.json', 'w')
    f.write(serialized_obj)
    f.close()
    
if __name__ == '__main__':
    snapshot_feyzin_data()
