import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot  # noqa: E402


def fix_flushed_lot_parents():
    lots = CarbureLot.objects.filter(delivery_type=CarbureLot.FLUSHED)
    print("> Found %d flushed lots" % lots.count())

    lots.update(parent_lot_id=None)
    print("> Removed parent lot from these lots")


if __name__ == "__main__":
    fix_flushed_lot_parents()
