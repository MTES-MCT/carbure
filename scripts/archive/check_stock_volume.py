import os

import django
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *


def check_volumes():
    stocks = CarbureStock.objects.all()
    for s in stocks:
        child = CarbureLot.objects.filter(parent_stock=s).values('volume').aggregate(sumvol=Sum('volume'))
        transfos = CarbureStockTransformation.objects.filter(source_stock=s).values('volume_deducted_from_source').aggregate(sumvol=Sum('volume_deducted_from_source'))
        sum_child = 0
        if child['sumvol'] is not None:
            sum_child = child['sumvol']
        if transfos['sumvol'] is not None:
            sum_child += transfos['sumvol']

        if s.parent_lot:
            theo_remaining_volume = s.parent_lot.volume - sum_child
            diff = theo_remaining_volume - s.remaining_volume
            if abs(diff) > 0.01:
                print('Stock %s theo remaining %.2f real remaining %.2f (id %d)' % (s.carbure_client.name, theo_remaining_volume, s.remaining_volume, s.id))




if __name__ == '__main__':
    check_volumes()

