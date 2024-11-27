import argparse
import os

import django

from transactions.sanity_checks.helpers import get_prefetched_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.core.paginator import Paginator  # noqa: E402
from django.db import transaction  # noqa: E402
from tqdm import tqdm  # noqa: E402

from core.models import CarbureLot  # noqa: E402
from transactions.sanity_checks.sanity_checks import bulk_scoring  # noqa: E402


@transaction.atomic
def data_reliability_scoring(year, batch):
    print("> Load all the declared lots of the year %s" % year)

    lots = (
        CarbureLot.objects.filter(year=year)
        .exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        .order_by("id")
        .select_related(
            "carbure_producer",
            "carbure_supplier",
            "carbure_client",
            "added_by",
            "carbure_production_site",
            "carbure_production_site__created_by",
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

    print(f"> Found {lots.count()} lots")

    paginator = Paginator(lots, batch)
    prefetched_data = get_prefetched_data()

    print(f"> Run scoring for lots (by batches of {batch})")
    for page_number in tqdm(paginator.page_range):
        page = paginator.page(page_number)
        page_lots = page.object_list
        bulk_scoring(page_lots, prefetched_data)


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
    args = parser.parse_args()
    data_reliability_scoring(args.year, args.batch)
