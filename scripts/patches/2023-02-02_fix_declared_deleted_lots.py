import os
import django
import argparse

from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot, CarbureLotEvent
from core.utils import generate_reports
from core.traceability import get_traceability_nodes, bulk_update_traceability_nodes, bulk_delete_traceability_nodes


@transaction.atomic
def fix_declared_deleted_lots(apply):
    deleted_events = CarbureLotEvent.objects.filter(event_type="DELETED").exclude(lot__lot_status="DELETED")
    print("> Found %d deleted events for declared lots" % deleted_events.count())

    deleted_ids = deleted_events.values_list("lot__id", flat=True)
    deleted_lots = CarbureLot.objects.filter(id__in=list(deleted_ids))

    lot_nodes = get_traceability_nodes(deleted_lots)

    deleted_nodes = []
    updated_nodes = []
    for node in lot_nodes:
        deleted, updated = node.delete()
        deleted_nodes += deleted
        updated_nodes += updated

    deleted_nodes = list(set(deleted_nodes))

    deleted_lots = []
    for node in deleted_nodes:
        if node.type == "LOT":
            deleted_lots.append(node.data)

    print("> Deleting those lots will propagate to a total of %d nodes" % (len(deleted_nodes) + len(updated_nodes)))

    if len(deleted_nodes) == 0:
        print("> No lots that should be deleted were found")
        return

    generate_reports("declared_deleted", deleted_lots)

    if apply:
        bulk_update_traceability_nodes(updated_nodes)
        bulk_delete_traceability_nodes(deleted_nodes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load ISCC certificates in database")
    parser.add_argument("--apply", dest="apply", action="store_true", default=False, help="Save the changes to the db")
    args = parser.parse_args()
    fix_declared_deleted_lots(args.apply)
