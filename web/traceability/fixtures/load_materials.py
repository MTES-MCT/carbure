import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from traceability.models import Material  # noqa: E402

filename = "%s/web/traceability/fixtures/materials.csv" % (os.environ["CARBURE_HOME"])


def cell(row, column):
    return (row.get(column) or "").strip() or None


with open(filename, newline="", encoding="utf-8-sig") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        code = cell(row, "code")
        name = cell(row, "name")
        if not code or not name:
            raise ValueError(f"Material row is missing code or name: {row}")

        Material.objects.update_or_create(
            code=code,
            defaults={"name": name},
        )
