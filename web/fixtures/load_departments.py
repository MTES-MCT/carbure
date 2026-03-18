import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Department, Region  # noqa: E402

filename = "%s/web/fixtures/csv/departments.csv" % (os.environ["CARBURE_HOME"])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    for row in reader:
        code_dept = row[0]
        if code_dept == "code":
            # header
            continue
        code = row[0]
        name = row[1]
        code_region = row[2]
        region = Region.objects.filter(code_region=code_region).first()

        obj, created = Department.objects.update_or_create(
            code_dept=code_dept,
            defaults={"name": name, "region": region},
        )
