import os
import django
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import *


def fix_lots_with_two_parents():
    lots = CarbureLot.objects.filter(parent_stock__isnull=False, parent_lot__isnull=False)
    print("Found %d lots with two parents" % (lots.count()))
    with transaction.atomic():
        for lot in lots:
            lot.parent_stock_id = None
            lot.save()


if __name__ == "__main__":
    fix_lots_with_two_parents()
