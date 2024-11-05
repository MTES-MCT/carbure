import argparse
import json
import os

import django
from django.core.paginator import Paginator
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot  # noqa: E402
from core.traceability import get_traceability_nodes  # noqa: E402


def check_integrity(year, batch=1000):
    print("> List root nodes for the year %s" % year)

    lots = (
        CarbureLot.objects.filter(year=year, parent_lot=None, parent_stock=None)
        .exclude(lot_status="DELETED")
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

    paginator = Paginator(lots, batch)

    all_errors = []
    error_count = 0
    lot_count = lots.count()

    print("> %d lots found" % lot_count)

    double_parent_lots = lots.filter(parent_lot_id__isnull=False, parent_stock_id__isnull=False)
    print("> Found %d lots with double lot/stock parents" % double_parent_lots.count())

    print("> Check traceability integrity of lots (by batches of %d)" % batch)
    for page_number in tqdm(paginator.page_range):
        page = paginator.page(page_number)
        page_lots = page.object_list
        nodes = get_traceability_nodes(page_lots)
        errors = [error for node in nodes for error in node.check_integrity()]
        all_errors += errors
        error_count += len(errors)

    print("> %d lots and %d errors found" % (lot_count, error_count))

    errors_by_node = {}
    for node, error, meta in all_errors:
        if node.data.id not in errors_by_node:
            errors_by_node[node.data.id] = {"node": node.serialize(), "errors": []}
        errors_by_node[node.data.id]["errors"].append({"error": error, "meta": meta})

    print("> Results:")
    print(json.dumps(errors_by_node, indent=2, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load ISCC certificates in database")
    parser.add_argument("--year", dest="year", action="store", default=None, help="Year to check")
    parser.add_argument("--batch", dest="batch", action="store", default=1000, help="Size of the db batches")
    args = parser.parse_args()
    check_integrity(args.year, args.batch)
