import argparse
import os
import django
from django.db import transaction
from django.db.models import Sum
from django.core.paginator import Paginator


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot, CarbureLotEvent, CarbureStock, CarbureStockEvent


@transaction.atomic
def recompute_stocks(apply, batch):

    all_stocks = (
        CarbureStock.objects.all()
        .order_by("id")
        .select_related("parent_lot", "parent_transformation")
        .prefetch_related("carburelot_set", "source_stock")
    )

    print(f"> Checking {all_stocks.count()} stocks")

    paginator = Paginator(all_stocks, per_page=batch)

    bad_count = 0

    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        page_stocks = page.object_list

        stocks_to_update = []
        update_events = []

        print(f"> Fixing batch {page_number} of {paginator.num_pages}...")

        for stock in page_stocks:
            initial_volume = 0
            if stock.parent_lot:
                initial_volume = stock.parent_lot.volume
            elif stock.parent_transformation:
                initial_volume = stock.parent_transformation.volume_destination

            total_lot_volume = stock.carburelot_set.exclude(lot_status=CarbureLot.DELETED).aggregate(Sum("volume"))
            total_transform_volume = stock.source_stock.aggregate(Sum("volume_deducted_from_source"))

            used_volume = (total_lot_volume["volume__sum"] or 0) + (
                total_transform_volume["volume_deducted_from_source__sum"] or 0
            )

            wanted_remaining_volume = round(initial_volume - used_volume, 2)
            current_remaining_volume = round(stock.remaining_volume, 2)

            if wanted_remaining_volume != current_remaining_volume:
                bad_count += 1

                delta = wanted_remaining_volume - current_remaining_volume

                print(f"#{stock.carbure_id} diff = {delta}")

                stock.remaining_volume = wanted_remaining_volume
                stock.remaining_lhv_amount = stock.get_lhv_amount()
                stock.remaining_weight = stock.get_weight()

                metadata = {"volume_diff": delta}
                update_event = CarbureStockEvent(event_type=CarbureLotEvent.UPDATED, stock=stock, metadata=metadata)

                stocks_to_update.append(stock)
                update_events.append(update_event)

        if apply:
            CarbureStock.objects.bulk_update(stocks_to_update, ["remaining_volume", "remaining_weight", "remaining_lhv_amount"])  # fmt:skip
            CarbureStockEvent.objects.bulk_create(update_events)

    print(f"> {bad_count} stocks with wrong remaining volumes were updated")

    print(f"> Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix stocks with wrong remaining volume")
    parser.add_argument("--apply", dest="apply", action="store_true", default=False, help="Save the changes to the db")
    parser.add_argument("--batch", dest="batch", action="store", type=int, default=1000, help="Size of the db batches")
    args = parser.parse_args()
    recompute_stocks(apply=args.apply, batch=args.batch)
