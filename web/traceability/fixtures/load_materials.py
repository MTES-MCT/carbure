import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from traceability.models import Material  # noqa: E402

filename = "%s/web/traceability/fixtures/materials.csv" % (os.environ["CARBURE_HOME"])


def cell(row, column):
    """Empty or missing cells become None. lhv and density are nullable; unit is not."""
    return (row.get(column) or "").strip() or None


with open(filename, newline="", encoding="utf-8-sig") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        code = cell(row, "code")
        name = cell(row, "name")
        lhv = cell(row, "lhv")
        density = cell(row, "density")
        unit = cell(row, "unit")
        if not code or not name or not unit:
            raise ValueError(f"Material row is missing code, name or unit: {row}")

        Material.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "lhv": lhv,
                "density": density,
                "unit": unit,
            },
        )

Material.objects.update_or_create(
    code=Material.VALORIZED_ENERGY_CODE,
    defaults={
        "name": Material.VALORIZED_ENERGY_NAME,
        "unit": Material.MJ,
        "lhv": None,
        "density": None,
    },
)
