import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.db import transaction  # noqa: E402
from django.db.models import Q  # noqa: E402

from core.models import CarbureLot, Depot, Entity  # noqa: E402


@transaction.atomic
def cleanup_fioul83_lots():
    fioul83 = Entity.objects.get(name="FIOUL83 EFPE")
    falaize = Entity.objects.get(name="FALAIZE ENERGIES ALTERNATIVES")
    right_depot = Depot.objects.get(name="Fioul 83 EFPE")

    wrong_depot_lots = CarbureLot.objects.exclude(lot_status="DELETED").filter(added_by=fioul83, carbure_client=falaize)
    wrong_depot_lots.update(carbure_delivery_site=right_depot)
    print("Changed delivery site to %s on %d lots" % (right_depot.name, wrong_depot_lots.count()))

    wrong_duplicated_filter = Q(added_by=fioul83) & (Q(unknown_supplier="Nord Ester") | Q(unknown_supplier="SAIPOL"))
    wrong_duplicated_lots = CarbureLot.objects.exclude(lot_status="DELETED").filter(wrong_duplicated_filter)
    print("Removed %d lots that were duplicated" % (wrong_duplicated_lots.count()))
    wrong_duplicated_lots.update(lot_status=CarbureLot.DELETED)


if __name__ == "__main__":
    cleanup_fioul83_lots()
