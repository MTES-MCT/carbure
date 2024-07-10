import argparse
import os
import django
from django.db import transaction
from django.db.models import F


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from transactions.services.carbure_id import bulk_generate_lot_carbure_id, bulk_generate_stock_carbure_id
from core.models import CarbureLot, CarbureStock


def update_carbure_id(apply, lots, stocks):
    if lots:
        update_carbure_id_for_lots(apply)

    if stocks:
        update_carbure_id_for_stocks(apply)


@transaction.atomic
def update_carbure_id_for_lots(apply):
    all_lots = CarbureLot.objects.all().exclude(lot_status=CarbureLot.DELETED)

    print(f"> Checking {all_lots.count()} lots")

    bad_id_lots = bulk_generate_lot_carbure_id(all_lots, save=apply)
    print(f"> {bad_id_lots.count()} lots with wrong id")

    print(f"> Done")


@transaction.atomic
def update_carbure_id_for_stocks(apply):
    all_stocks = CarbureStock.objects.all().select_related("parent_lot", "production_country", "depot").order_by("id")

    print(f"> Checking {all_stocks.count()} stocks")

    bad_id_stocks = bulk_generate_stock_carbure_id(all_stocks, save=apply)
    print(f"> {bad_id_stocks.count()} stocks with wrong id")

    print(f"> Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix lots with carbure_id disconnected from the actual lot state")
    parser.add_argument("--apply", dest="apply", action="store_true", default=False, help="Save the changes to the db")
    parser.add_argument("--lots", dest="lots", action="store_true", default=False, help="Update lots")
    parser.add_argument("--stocks", dest="stocks", action="store_true", default=False, help="Update stocks")
    args = parser.parse_args()
    update_carbure_id(apply=args.apply, lots=args.lots, stocks=args.stocks)
