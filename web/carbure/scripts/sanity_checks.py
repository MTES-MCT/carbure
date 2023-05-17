import argparse
import django
import os
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.core.paginator import Paginator
from django.db import transaction
from tqdm import tqdm

from core.models import CarbureLot, GenericError
from api.v4.sanity_checks import bulk_sanity_checks
from api.v4.helpers import get_prefetched_data


@transaction.atomic
def cleanup_sanity_checks(year, batch, apply):
    print("> Load all the declared lots of the year %s" % year)

    previous_errors = GenericError.objects.filter(lot__year=year)
    previous_warning_count = previous_errors.filter(is_blocking=False).count()
    previous_error_count = previous_errors.filter(is_blocking=True).count()

    print(
        "> Before the modification, there are %d errors and %d warnings detected"
        % (previous_error_count, previous_warning_count)
    )

    lots = (
        CarbureLot.objects.filter(year=year)
        .filter(lot_status__in=(CarbureLot.ACCEPTED, CarbureLot.FROZEN, CarbureLot.PENDING))
        .order_by("id")
        .select_related(
            "carbure_producer",
            "carbure_supplier",
            "carbure_client",
            "added_by",
            "carbure_production_site",
            "carbure_production_site__producer",
            "carbure_production_site__country",
            "production_country",
            "carbure_dispatch_site",
            "carbure_dispatch_site__country",
            "dispatch_site_country",
            "carbure_delivery_site",
            "carbure_delivery_site__country",
            "delivery_site_country",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "parent_stock",
            "parent_lot",
        )
    )

    lot_count = lots.count()

    print("> Found %d lots" % lot_count)

    paginator = Paginator(lots, batch)

    all_warnings = []
    all_errors = []

    prefetched_data = get_prefetched_data()

    print("> Run sanity checks for lots (by batches of %d)" % batch)
    for page_number in tqdm(paginator.page_range):
        page = paginator.page(page_number)
        page_lots = page.object_list
        errors = bulk_sanity_checks(page_lots, prefetched_data, dry_run=not apply)
        all_warnings += [warning for warning in errors if not warning.is_blocking]
        all_errors += [error for error in errors if error.is_blocking]

    print("> Found %d errors and %d warnings" % (len(all_errors), len(all_warnings)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run sanity checks on all the lots of a given year")
    parser.add_argument("--year", dest="year", action="store", default=None, help="Year to check")
    parser.add_argument("--batch", dest="batch", action="store", default=1000, help="Size of the db batches")
    parser.add_argument("--apply", dest="apply", action="store_true", default=False, help="Save the changes to the db")
    args = parser.parse_args()
    cleanup_sanity_checks(args.year, args.batch, args.apply)
