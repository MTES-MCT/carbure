import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *  # noqa: E402


def fix_stocks():
    odd_lots = CarbureLot.objects.filter(parent_lot__isnull=False, parent_stock__isnull=False)
    for l in odd_lots:
        print("fix lot %d" % (l.id))
        l.parent_stock = None
        l.save()


if __name__ == "__main__":
    fix_stocks()
