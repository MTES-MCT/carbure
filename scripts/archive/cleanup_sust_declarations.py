import calendar
import datetime
import os

import django
from django.db.models import Count

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import *  # noqa: E402


def fix_declaration_deadlines():
    decs = SustainabilityDeclaration.objects.all()
    for d in decs:
        nextmonth = d.period + datetime.timedelta(days=31)
        (weekday, lastday) = calendar.monthrange(nextmonth.year, nextmonth.month)
        deadline = datetime.date(year=nextmonth.year, month=nextmonth.month, day=lastday)
        if deadline != d.deadline:
            print("Declaration %s for %s is wrong: deadline: %s - theo %s" % (d.entity.name, d.period, d.deadline, deadline))
            d.deadline = deadline
            d.save()


def fix_declaration_duplicates():
    summary = SustainabilityDeclaration.objects.values("entity", "period").annotate(count=Count("period"))
    for d in summary:
        if d["count"] > 1:
            print(d)
            # keep only the first one
            declarations = SustainabilityDeclaration.objects.filter(entity_id=d["entity"], period=d["period"]).order_by("id")
            min_id = declarations[0].id
            to_delete = declarations.exclude(id=min_id)
            to_delete.delete()


if __name__ == "__main__":
    fix_declaration_deadlines()
    fix_declaration_duplicates()
