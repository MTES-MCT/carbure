import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from traceability.models import Material  # noqa: E402

filename = "%s/web/traceability/fixtures/materials.csv" % (os.environ["CARBURE_HOME"])

with open(filename, newline="", encoding="utf-8-sig") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        code = row["code"].strip()
        name = row["name"].strip()
        lhv = row["lhv"].strip() or None
        density = row["density"].strip() or None

        Material.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "lhv": lhv,
                "density": density,
            },
        )
