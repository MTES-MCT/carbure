import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.core.paginator import Paginator
from django.db import transaction
from tqdm import tqdm

from core.models import CarbureLot, SustainabilityDeclaration


@transaction.atomic
def sync_declarations_with_lot_status(batch_size=1000):
    print("> List all declarations, validated and unvalidated")
    declarations = SustainabilityDeclaration.objects.filter(period__year__gte=2021)

    print("> Found %d declarations" % declarations.count())

    declarations_by_entity = {}
    for declaration in declarations:
        entity_id = declaration.entity_id
        period = declaration.period.year * 100 + declaration.period.month

        if entity_id not in declarations_by_entity:
            declarations_by_entity[entity_id] = {}

        declarations_by_entity[entity_id][period] = declaration

    # only treat lots that are already accepted or declared starting from 2021
    lots = (
        CarbureLot.objects.filter(year__gte=2021)
        .filter(lot_status__in=(CarbureLot.ACCEPTED, CarbureLot.FROZEN))
        .order_by("delivery_date")
    )

    paginator = Paginator(lots, batch_size)

    print("> Set lot declaration state according to period declaration state")

    for page_number in tqdm(paginator.page_range):
        page = paginator.page(page_number)
        page_lots = page.object_list

        for lot in page_lots:
            # find the declarations
            supplier_declaration = declarations_by_entity.get(lot.carbure_supplier_id, {}).get(lot.period, None)
            client_declaration = declarations_by_entity.get(lot.carbure_client_id, {}).get(lot.period, None)

            # set the lot declaration status according to the related declaration status
            if supplier_declaration:
                lot.declared_by_supplier = supplier_declaration.declared

            if client_declaration:
                lot.declared_by_client = client_declaration.declared

            # handle the case of lots with unknown clients or suppliers
            if not lot.carbure_client_id:
                lot.declared_by_client = lot.declared_by_supplier

            if not lot.carbure_supplier_id:
                lot.declared_by_supplier = lot.declared_by_client

            if lot.declared_by_supplier and lot.declared_by_client:
                lot.lot_status = CarbureLot.FROZEN
            else:
                lot.lot_status = CarbureLot.ACCEPTED

        CarbureLot.objects.bulk_update(page_lots, ["lot_status", "declared_by_supplier", "declared_by_client"])

    print("> Done")


if __name__ == "__main__":
    sync_declarations_with_lot_status()


def generate_report():
    pass
