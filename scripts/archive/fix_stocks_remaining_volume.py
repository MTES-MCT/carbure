import os

import django
from django.db import transaction
from django.db.models import Sum
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import *


def fix_stocks_remaining_volume():
    stocks = CarbureStock.objects.all()
    with transaction.atomic():
        for stock in tqdm(stocks):
            child_volume = (
                CarbureLot.objects.filter(parent_stock=stock)
                .exclude(lot_status=CarbureLot.DELETED)
                .aggregate(child_volume=Sum("volume"))
            )
            vol = child_volume["child_volume"]
            if vol is None:
                vol = 0
            transformations_volume = CarbureStockTransformation.objects.filter(source_stock=stock).aggregate(
                vol=Sum("volume_deducted_from_source")
            )
            if transformations_volume["vol"] is not None:
                vol += transformations_volume["vol"]
            initial_volume = stock.parent_lot.volume if stock.parent_lot else stock.parent_transformation.volume_destination
            theo_remaining = initial_volume - vol
            if stock.remaining_volume != theo_remaining:
                stock.remaining_volume = round(theo_remaining, 2)
                stock.remaining_weight = stock.get_weight()
                stock.remaining_lhv_amount = stock.get_lhv_amount()
                stock.save()


if __name__ == "__main__":
    fix_stocks_remaining_volume()
