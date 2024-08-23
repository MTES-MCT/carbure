import argparse
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot
from saf.models.saf_ticket_source import create_ticket_sources_from_lots


def create_ticket_sources_from_declared_lots(year):
    lots = CarbureLot.objects.select_related("biofuel").filter(year=year, carbure_client_id__isnull=False)

    ticket_sources = create_ticket_sources_from_lots(lots)
    entities = ticket_sources.values_list("added_by__name", flat=True).distinct()

    print("[SAF] %d ticket sources created for %s" % (len(ticket_sources), ", ".join(list(set(entities)))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create SAF ticket sources based on validated SAF lots")
    parser.add_argument("--year", dest="year", default=False, help="Pick the year to focus on")
    args = parser.parse_args()

    if not args.year:
        raise Exception("A year must be provided")

    create_ticket_sources_from_declared_lots(year=int(args.year))
