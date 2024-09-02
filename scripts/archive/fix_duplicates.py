import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *  # noqa: E402


def fix_duplicates():
    odd_lots = CarbureLot.objects.filter(parent_lot__delivery_type=CarbureLot.BLENDING)
    for lot in odd_lots:
        if lot.parent_lot.carbure_client != lot.carbure_client:
            print(
                "%d %d not duplicates (%s %s)"
                % (lot.parent_lot.id, lot.id, lot.parent_lot.carbure_client, lot.carbure_client)
            )
            lot.parent_lot.delivery_type = CarbureLot.TRADING
            lot.parent_lot.save()
        else:
            print("%d %d duplicates" % (lot.parent_lot.id, lot.id))
            lot.delete()


if __name__ == "__main__":
    fix_duplicates()
