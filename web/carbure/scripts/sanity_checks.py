import argparse
import os
from typing import Iterable

import django

from transactions.sanity_checks.helpers import get_prefetched_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.core.paginator import Paginator  # noqa: E402
from django.db import transaction  # noqa: E402
from tqdm import tqdm  # noqa: E402

from core.models import CarbureLot, GenericError  # noqa: E402
from transactions.sanity_checks.sanity_checks import bulk_sanity_checks  # noqa: E402


@transaction.atomic
def cleanup_sanity_checks(year, batch, apply):
    print("> Load all the declared lots of the year %s" % year)

    batch = int(batch)

    previous_errors = GenericError.objects.filter(lot__year=year)
    previous_warnings = previous_errors.filter(is_blocking=False)
    previous_errors = previous_errors.filter(is_blocking=True)

    print(
        f"> Before the modification, there are {previous_errors.count()} errors and {previous_warnings.count()} warnings detected"  # noqa: E501
    )

    show_error_details(previous_errors, "error")
    show_error_details(previous_warnings, "warning")

    lots = (
        CarbureLot.objects.filter(year=year)
        .filter(lot_status__in=[CarbureLot.DRAFT, CarbureLot.ACCEPTED, CarbureLot.FROZEN, CarbureLot.PENDING])
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

    show_error_details(all_errors, "error")
    show_error_details(all_warnings, "warning")


def show_error_details(errors: Iterable[GenericError], type: str):
    by_error: dict[str, int] = {}
    for error in errors:
        if error.error not in by_error:
            by_error[error.error] = 0
        by_error[error.error] += 1

    error_count = list(by_error.items())
    error_count.sort(key=lambda err: err[1])
    error_count = list(reversed(error_count))

    print(f"> Show number of {type} per type:")
    for error, count in error_count:
        print(f"  - {error}: {count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run sanity checks on all the lots of a given year")
    parser.add_argument("--year", dest="year", action="store", default=None, help="Year to check")
    parser.add_argument(
        "--batch",
        dest="batch",
        action="store",
        default=1000,
        help="Size of the db batches",
    )
    parser.add_argument(
        "--apply",
        dest="apply",
        action="store_true",
        default=False,
        help="Save the changes to the db",
    )
    args = parser.parse_args()
    cleanup_sanity_checks(args.year, args.batch, args.apply)
