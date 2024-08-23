import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot


def cleanup_lagelouze_mac():
    lots = CarbureLot.objects.filter(year=2021, delivery_type=CarbureLot.RFC, carbure_client__name="LAGELOUZE")
    lots.update(delivery_type=CarbureLot.BLENDING)


if __name__ == "__main__":
    cleanup_lagelouze_mac()
