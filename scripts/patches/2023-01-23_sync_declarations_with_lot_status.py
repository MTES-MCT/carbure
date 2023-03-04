import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from tqdm import tqdm
from django.db import transaction
from core.models import CarbureLot, SustainabilityDeclaration


@transaction.atomic
def sync_declarations_with_lot_status():
    print("> Set lot declaration state according to period declaration state")
    for declaration in tqdm(SustainabilityDeclaration.objects.all()):
        entity_id = declaration.entity_id
        period = declaration.period.year * 100 + declaration.period.month

        period_lots = CarbureLot.objects.filter(period=period).exclude(lot_status__in=(CarbureLot.DRAFT, CarbureLot.DELETED))  # fmt:skip

        sent_lots = period_lots.filter(carbure_supplier_id=entity_id)
        sent_lots_with_unknown_client = sent_lots.filter(carbure_client=None)

        received_lots = period_lots.filter(carbure_client_id=entity_id)
        received_lots_with_unknown_supplier = received_lots.filter(carbure_supplier=None)

        if declaration.declared:
            sent_lots.update(declared_by_supplier=True)
            sent_lots_with_unknown_client.update(declared_by_client=True)
            received_lots.update(declared_by_client=True)
            received_lots_with_unknown_supplier.update(declared_by_supplier=True)
        else:
            sent_lots.update(declared_by_supplier=False)
            sent_lots_with_unknown_client.update(declared_by_client=False)
            received_lots.update(declared_by_client=False)
            received_lots_with_unknown_supplier.update(declared_by_supplier=False)

    print("> Set lot status according to lot declaration state")
    lots = CarbureLot.objects.exclude(lot_status__in=(CarbureLot.DRAFT, CarbureLot.DELETED))

    declared_lots = lots.filter(declared_by_supplier=True, declared_by_client=True)
    declared_lots.update(lot_status=CarbureLot.FROZEN)

    undeclared_lots = lots.filter(lot_status=CarbureLot.FROZEN).exclude(declared_by_supplier=True, declared_by_client=True)  # fmt:skip
    undeclared_lots.update(lot_status=CarbureLot.ACCEPTED)

    print("> Done")


if __name__ == "__main__":
    sync_declarations_with_lot_status()


def generate_report():
    pass
