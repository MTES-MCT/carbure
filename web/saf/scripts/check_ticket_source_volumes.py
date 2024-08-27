import argparse
import os

import django
from django.db.models import Sum
from django.db.models.functions import Coalesce

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from saf.models.saf_ticket_source import SafTicketSource  # noqa: E402


def check_ticket_source_volumes(year, fix):
    ticket_sources = SafTicketSource.objects.annotate(used_volume=Coalesce(Sum("saf_tickets__volume"), 0.0))
    if year is not None:
        ticket_sources = ticket_sources.filter(year=int(year))

    errors = []
    for ticket_source in ticket_sources:
        if ticket_source.used_volume > ticket_source.total_volume:
            errors.append({"error": "TOO_MUCH_VOLUME_USED", "ticket_source": ticket_source})
        if ticket_source.used_volume != ticket_source.assigned_volume:
            errors.append({"error": "ASSIGNED_VOLUME_INCORRECT", "ticket_source": ticket_source})

    print(f"> There are {len(errors)} problems with SAF tickets")

    fixed_ticket_sources = []

    for error in errors:
        err = error["error"]
        ts = error["ticket_source"]

        if err == "TOO_MUCH_VOLUME_USED":
            print(f"{error['error']}: {ts.added_by.name} {ts.carbure_id} => {ts.total_volume} < {ts.used_volume}")

        if err == "ASSIGNED_VOLUME_INCORRECT":
            print(f"{error['error']}: {ts.added_by.name} {ts.carbure_id} => {ts.assigned_volume} ≠ {ts.used_volume}")
            if fix:
                ts.assigned_volume = ts.used_volume
                fixed_ticket_sources.append(ts)

    if fix:
        SafTicketSource.objects.bulk_update(fixed_ticket_sources, ["assigned_volume"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create SAF ticket sources based on validated SAF lots")
    parser.add_argument("--year", dest="year", default=None, help="Pick the year to focus on")
    parser.add_argument("--fix", dest="fix", action="store_true", help="Fix solveable problems")
    args = parser.parse_args()
    check_ticket_source_volumes(year=args.year, fix=args.fix)
