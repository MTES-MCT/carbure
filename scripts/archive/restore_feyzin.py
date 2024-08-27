import os

import django
from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.core import serializers  # noqa: E402

from core.models import *  # noqa: E402


def load_feyzin_data():
    feyzin = Entity.objects.get(name="TERF Feyzin")

    transactions = {tx.id: tx for tx in LotTransaction.objects.filter(Q(carbure_client=feyzin) | Q(carbure_vendor=feyzin))}
    lots = {l.id: l for l in LotV2.objects.filter(id__in=transactions.keys())}

    prev_lots = {}
    f = open("lots.json", "r")
    it = serializers.deserialize("json", f)
    for obj in it:
        prev_lots[obj.object.id] = obj
    f.close()

    prev_transactions = []
    f = open("transactions.json", "r")
    it = serializers.deserialize("json", f)
    for obj in it:
        prev_transactions.append(obj)
    f.close()

    for tx in prev_transactions:
        if tx.object.id not in transactions:
            # ensure lot exists
            if tx.object.lot_id not in lots:
                print("creating associated lot")
                prev_lot = prev_lots[tx.object.lot_id]
                prev_lot.save()
            else:
                print("lot already in db")
            tx.save()


if __name__ == "__main__":
    load_feyzin_data()
