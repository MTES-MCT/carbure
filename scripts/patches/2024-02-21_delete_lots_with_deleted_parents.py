import argparse
import os
import django
from django.db import transaction


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.utils import generate_reports
from core.models import CarbureLot, CarbureLotEvent


@transaction.atomic
def delete_lots_with_deleted_parents(apply, batch):
    lots_to_delete = CarbureLot.objects.exclude(lot_status=CarbureLot.DELETED).filter(parent_lot__lot_status=CarbureLot.DELETED)  # fmt:skip

    comment = "Ces lots auraient déjà dû être supprimés, étant donné que leurs parents l'avaient été."
    deletion_events = [CarbureLotEvent(event_type=CarbureLotEvent.DELETED_BY_ADMIN, lot=lot, metadata=comment) for lot in lots_to_delete]  # fmt:skip

    generate_reports("lots à supprimer", lots_to_delete)

    if apply:
        lots_to_delete.update(lot_status=CarbureLot.DELETED)
        CarbureLotEvent.objects.bulk_create(deletion_events)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update feedstock --id --name --code")
    parser.add_argument("--apply", dest="apply", action="store_true", default=False, help="Save the changes to the db")
    parser.add_argument("--batch", dest="batch", action="store", default=1000)
    args = parser.parse_args()
    delete_lots_with_deleted_parents(apply=args.apply, batch=args.batch)
