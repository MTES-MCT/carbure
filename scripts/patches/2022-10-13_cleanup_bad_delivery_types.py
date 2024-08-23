import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot

ok_delivery_types = (
    CarbureLot.UNKNOWN,
    CarbureLot.RFC,
    CarbureLot.STOCK,
    CarbureLot.BLENDING,
    CarbureLot.EXPORT,
    CarbureLot.TRADING,
    CarbureLot.PROCESSING,
    CarbureLot.DIRECT,
    CarbureLot.FLUSHED,
)


def cleanup_bad_delivery_types():
    lots = CarbureLot.objects.exclude(delivery_type__in=ok_delivery_types)
    lot_ids = list(lots.values_list("id", flat=True))
    CarbureLot.objects.filter(id__in=lot_ids).update(delivery_type=CarbureLot.UNKNOWN)


if __name__ == "__main__":
    cleanup_bad_delivery_types()
