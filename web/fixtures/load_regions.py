import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Region  # noqa: E402

filename = "%s/web/fixtures/csv/regions.csv" % (os.environ["CARBURE_HOME"])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    for row in reader:
        code_region = row[0]
        if code_region == "code":
            # header
            continue
        code = row[0]
        name = row[1]
        obj, created = Region.objects.update_or_create(
            code_region=code_region,
            defaults={"name": name},
        )
