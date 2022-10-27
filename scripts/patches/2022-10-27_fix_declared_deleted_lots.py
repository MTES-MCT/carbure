import os
import django
from django.db import transaction
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot, CarbureLotEvent


@transaction.atomic
def fix_declared_deleted_lots():

    deleted_events = CarbureLotEvent.objects.filter(event_type="DELETED").exclude(lot__lot_status="DELETED")
    print("%d deleted events found for declared lots" % deleted_events.count())

    deleted_ids = deleted_events.values_list("lot__id", flat=True)
    deleted_lots = CarbureLot.objects.filter(id__in=deleted_events.values("lot__id"))

    possible_dups = CarbureLot.objects.exclude(Q(id__in=deleted_ids) | Q(lot_status="DELETED")).filter(
        added_by_id__in=deleted_lots.values("added_by_id"),
        transport_document_reference__in=deleted_lots.values("transport_document_reference"),
    )

    summary = (
        CarbureLot.objects.exclude(id__in=deleted_ids)
        .exclude(lot_status="DELETED")
        .filter(transport_document_reference__in=deleted_lots.values("transport_document_reference"))
        .values("transport_document_reference", "lot_status", "added_by__name", "volume", "delivery_date")
        .annotate(count=Count("id"))
        .values_list(
            "lot_status",
            "added_by__name",
            "transport_document_reference",
            "count",
        )
        .order_by("count")
    )

    print("%d results" % summary.count())
    print(summary.aggregate(Sum("count")))

    for bla in summary:
        print(bla)


if __name__ == "__main__":
    fix_declared_deleted_lots()
