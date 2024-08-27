import argparse
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.core.paginator import Paginator
from django.db import transaction
from tqdm import tqdm

from certificates.models import DoubleCountingRegistration
from core.models import CarbureLot
from transactions.sanity_checks import bulk_sanity_checks


@transaction.atomic
def pick_right_dc_agreements(from_year=2021, batch=1000):
    changed_count = 0

    lots = (
        CarbureLot.objects.filter(delivery_date__year__gte=from_year)
        .exclude(lot_status=CarbureLot.DELETED)
        .exclude(production_site_double_counting_certificate=None)
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

    dc_agreements = (
        DoubleCountingRegistration.objects.filter(valid_until__year__gte=from_year)
        .select_related("production_site")
        .order_by("valid_from")
    )

    dc_agreements_by_psite = {}
    dc_agreements_by_number = {}

    for dc_agreement in dc_agreements:
        dc_number = get_dc_number(dc_agreement.certificate_id)
        if dc_number not in dc_agreements_by_number:
            dc_agreements_by_number[dc_number] = []
        dc_agreements_by_number[dc_number].append(dc_agreement)

        if dc_agreement.production_site is None:
            continue

        psite = dc_agreement.production_site.pk
        if psite not in dc_agreements_by_psite:
            dc_agreements_by_psite[psite] = []

        dc_agreements_by_psite[psite].append(dc_agreement)

    print(f"> Found {lots.count()} lots with a DC certificate")

    paginator = Paginator(lots, batch)

    for page_number in tqdm(paginator.page_range):
        page = paginator.page(page_number)
        page_lots = page.object_list

        changed = []

        for lot in page_lots:
            new_agreement = None
            old_agreement = lot.production_site_double_counting_certificate or None

            psite_dc_agreements = dc_agreements_by_psite.get(get_psite(lot), [])
            number_dc_agreements = dc_agreements_by_number.get(get_dc_number(old_agreement), [])

            for psite_dc_agreement in psite_dc_agreements + number_dc_agreements:
                if psite_dc_agreement.valid_from < lot.delivery_date and psite_dc_agreement.valid_until >= lot.delivery_date:
                    new_agreement = psite_dc_agreement.certificate_id
                    break

            if not lot.feedstock or not lot.feedstock.is_double_compte:
                new_agreement = None

            if (new_agreement or old_agreement) and new_agreement != old_agreement:
                # print(f"* Change [{lot.pk}] {old_agreement} => {new_agreement} ({lot.delivery_date})")
                lot.production_site_double_counting_certificate = new_agreement
                changed.append(lot)

        changed_count += len(changed)
        CarbureLot.objects.bulk_update(changed, ["production_site_double_counting_certificate"])

    bulk_sanity_checks(lots)
    print(f"> Fixed {changed_count} lots with a wrong DC agreement")


def get_psite(lot: CarbureLot):
    if not lot.carbure_production_site:
        return None
    return lot.carbure_production_site.pk


def get_dc_number(certificate_id: str):
    try:
        return certificate_id.split("_")[1]
    except:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix lots that have the wrong dc agreement selected")
    parser.add_argument(
        "--from-year", dest="from_year", action="store", default=2021, help="From which year to start checking"
    )
    parser.add_argument("--batch", dest="batch", action="store", default=1000, help="How many lots processed at once")
    args = parser.parse_args()
    pick_right_dc_agreements(args.from_year, args.batch)
