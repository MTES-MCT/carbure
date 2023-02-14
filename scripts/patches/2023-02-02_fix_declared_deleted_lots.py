import os
import django
import argparse

from django.db import transaction
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot, CarbureLotEvent


@transaction.atomic
def fix_declared_deleted_lots(apply):
    deleted_events = CarbureLotEvent.objects.filter(event_type="DELETED").exclude(lot__lot_status="DELETED")
    print("> Found %d deleted events for declared lots" % deleted_events.count())

    deleted_ids = deleted_events.values_list("lot__id", flat=True)
    deleted_lots = CarbureLot.objects.filter(id__in=list(deleted_ids))

    if deleted_lots.count() == 0:
        print("> No matching lots found for these events")
        return

    if apply:
        deleted_lots.update(lot_status=CarbureLot.DELETED)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load ISCC certificates in database")
    parser.add_argument("--apply", dest="apply", action="store_true", default=False, help="Save the changes to the db")
    args = parser.parse_args()
    fix_declared_deleted_lots(args.apply)
