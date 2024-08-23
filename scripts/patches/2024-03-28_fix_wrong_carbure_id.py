import argparse
import os

import django
from django.core.paginator import Paginator
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot, CarbureLotEvent


@transaction.atomic
def fix_wrong_carbure_id(apply, batch):
    all_lots = (
        CarbureLot.objects.all()
        .exclude(lot_status=CarbureLot.DELETED)
        .select_related("production_country", "carbure_delivery_site")
        .order_by("id")
    )

    print(f"> Checking {all_lots.count()} lots")

    paginator = Paginator(all_lots, per_page=batch)

    bad_count = 0

    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        page_lots = page.object_list

        lots_to_update = []
        update_events = []

        print(f"> Fixing batch {page_number} of {paginator.num_pages}...")

        for lot in page_lots:
            old_carbure_id = lot.carbure_id
            lot.generate_carbure_id()

            if lot.carbure_id != old_carbure_id:
                bad_count += 1
                metadata = {"added": [], "removed": [], "changed": [["carbure_id", old_carbure_id, lot.carbure_id]]}
                update_event = CarbureLotEvent(event_type=CarbureLotEvent.UPDATED, lot=lot, metadata=metadata)
                lots_to_update.append(lot)
                update_events.append(update_event)

        if apply:
            CarbureLot.objects.bulk_update(lots_to_update, ["carbure_id"])
            CarbureLotEvent.objects.bulk_create(update_events)

    print(f"> {bad_count} lots with wrong carbure_id were updated")

    print("> Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix lots with carbure_id disconnected from the actual lot state")
    parser.add_argument("--apply", dest="apply", action="store_true", default=False, help="Save the changes to the db")
    parser.add_argument("--batch", dest="batch", action="store", type=int, default=1000, help="Size of the db batches")
    args = parser.parse_args()
    fix_wrong_carbure_id(apply=args.apply, batch=args.batch)
