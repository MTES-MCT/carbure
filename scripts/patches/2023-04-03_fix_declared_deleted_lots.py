import argparse
import os

import django
from django.db import transaction
from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot, CarbureLotEvent  # noqa: E402
from core.traceability import (
    bulk_delete_traceability_nodes,
    bulk_update_traceability_nodes,
    get_traceability_nodes,
)  # noqa: E402
from core.utils import generate_reports  # noqa: E402


@transaction.atomic
def fix_declared_deleted_lots(apply):
    deleted_events = CarbureLotEvent.objects.filter(event_type="DELETED").exclude(lot__lot_status="DELETED")
    print("> Found %d deleted events for declared lots" % deleted_events.count())

    deleted_ids = deleted_events.values_list("lot__id", flat=True)
    deleted_lots = CarbureLot.objects.filter(id__in=list(deleted_ids))

    lots_to_delete = deleted_lots.exclude(Q(added_by_id=4) | Q(id=924502))
    print(f"> A total of {lots_to_delete.count()} lots will be deleted")

    lots_to_update = deleted_lots.filter(added_by_id=4).exclude(id=160764)
    print(f"> A total of {lots_to_update.count()} lots will be updated")

    lots_with_events_to_delete = deleted_lots.filter(Q(added_by_id=4) | Q(id=924502))
    events_to_delete = CarbureLotEvent.objects.filter(lot__in=lots_with_events_to_delete, event_type="DELETED")
    print(f"> A total of {events_to_delete.count()} wrong DELETE events will be removed")

    deleted_nodes = []
    updated_nodes = []

    # prepare analysis of traceability for updating the relevant lots
    lot_nodes_to_update = get_traceability_nodes(lots_to_update)

    for node in lot_nodes_to_update:
        # apply the update to the lot
        node.update({"supplier_certificate": "2BS010181", "production_site_certificate": "2BS010001"})

        # if the node changed, recursively apply the update to related nodes
        if len(node.diff) > 0:
            updated_nodes += node.propagate(changed_only=True)

    print(f"> Updating those lots will propagate to a total of {len(updated_nodes)} nodes")

    # prepare analysis of traceability for deleting the relevant lots
    lot_nodes_to_delete = get_traceability_nodes(lots_to_delete)

    for node in lot_nodes_to_delete:
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
        events_to_delete.delete()
        bulk_update_traceability_nodes(updated_nodes)
        bulk_delete_traceability_nodes(deleted_nodes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix lots that were deleted but reappeared after a bug")
    parser.add_argument("--apply", dest="apply", action="store_true", default=False, help="Save the changes to the db")
    args = parser.parse_args()
    fix_declared_deleted_lots(args.apply)
