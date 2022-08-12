import os
import django
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import *


def calculate_older_quantities():
    lots_without_alt_quantities = CarbureLot.objects.filter(weight=0)
    print('Found %d lots without alt quantities' % (lots_without_alt_quantities.count()))
    with transaction.atomic():
        for lot in lots_without_alt_quantities.iterator():
            lot.weight = lot.get_weight()
            lot.lhv_amount = lot.get_lhv_amount()
            lot.save()


if __name__ == '__main__':
    calculate_older_quantities()
