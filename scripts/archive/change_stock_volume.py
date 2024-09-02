import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *  # noqa: E402


def change_stock_volume(stock_id, volume):
    s = CarbureStock.objects.get(id=stock_id)
    s.remaining_volume = volume
    s.remaining_lhv_amount = s.get_lhv_amount()
    s.remaining_weight = s.get_weight()
    s.save()
    print(s.remaining_volume, s.remaining_lhv_amount, s.remaining_weight)


if __name__ == "__main__":
    change_stock_volume(1275, 855017)
