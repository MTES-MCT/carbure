import argparse
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot
from saf.models.saf_ticket_source import SafTicketSource, create_ticket_source_from_lot


# list of accepted SAF
SAF = ("HVOC", "HOC", "HCC")


def create_ticket_sources_from_declared_lots(year):
    lots = CarbureLot.objects.select_related("biofuel").filter(
        lot_status=CarbureLot.FROZEN, year=year, biofuel__code__in=SAF, carbure_client_id__isnull=False
    )

    entities = lots.values_list("carbure_client__name", flat=True).distinct()

    ticket_sources = []
    for lot in lots.iterator():
        ticket_sources.append(create_ticket_source_from_lot(lot))

    created = SafTicketSource.objects.bulk_create(ticket_sources)
    print("[SAF] %d ticket sources created for %s" % (len(created), ", ".join(list(entities))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load ISCC certificates in database")
    parser.add_argument("--year", dest="year", default=False, help="Pick the year to focus on")
    args = parser.parse_args()

    if not args.year:
        raise Exception("A year must be provided")

    create_ticket_sources_from_declared_lots(year=int(args.year))
