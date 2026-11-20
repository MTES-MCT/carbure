import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.utils import bulk_update_or_create  # noqa: E402
from traceability.models import Material  # noqa: E402

filename = "%s/web/traceability/fixtures/materials.csv" % (os.environ["CARBURE_HOME"])


def cell(row, column):
    """Empty or missing cells become None. lhv and density are nullable; unit is not."""
    return (row.get(column) or "").strip() or None


materials_by_code = {}
with open(filename, newline="", encoding="utf-8-sig") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        material = {
            "code": cell(row, "code"),
            "name": cell(row, "name"),
            "lhv": cell(row, "lhv"),
            "density": cell(row, "density"),
            "unit": cell(row, "unit"),
        }

        if not material["code"] or not material["name"] or not material["unit"]:
            raise ValueError(f"Material row is missing code, name or unit: {row}")

        materials_by_code[material["code"]] = material

bulk_update_or_create(Material, "code", list(materials_by_code.values()))
