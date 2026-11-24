import csv
import os

import django
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.utils import bulk_update_or_create  # noqa: E402
from traceability.models import Material, MaterialTag  # noqa: E402
from traceability.models.material_tag import Tag  # noqa: E402

filename = "%s/web/traceability/fixtures/materials.csv" % (os.environ["CARBURE_HOME"])


def cell(row, column):
    """Empty or missing cells become None. lhv and density are nullable; unit is not."""
    return (row.get(column) or "").strip() or None


def sync_tags(material_tags, tag_columns):
    material_ids = dict(Material.objects.filter(code__in=material_tags).values_list("code", "id"))
    missing_tags = {
        (material_ids[code], tag_type, value)
        for code, tags in material_tags.items()
        for tag_type, values in tags.items()
        for value in values
    }

    existing_tags = MaterialTag.objects.filter(material_id__in=material_ids.values(), type__in=tag_columns).order_by("pk")
    obsolete_ids = []
    for tag in existing_tags:
        key = (tag.material_id, tag.type, tag.value)
        if key in missing_tags:
            missing_tags.remove(key)
        else:
            obsolete_ids.append(tag.pk)

    MaterialTag.objects.filter(pk__in=obsolete_ids).delete()
    MaterialTag.objects.bulk_create(
        [MaterialTag(material_id=material_id, type=tag_type, value=value) for material_id, tag_type, value in missing_tags]
    )


materials = {}
material_tags = {}

with open(filename, newline="", encoding="utf-8-sig") as csvfile:
    reader = csv.DictReader(csvfile)

    # Find CSV columns matching a known tag type
    tag_columns = set(reader.fieldnames or ()) & set(Tag.values)

    for row in reader:
        code = cell(row, "code")
        name = cell(row, "name")
        lhv = cell(row, "lhv")
        density = cell(row, "density")
        unit = cell(row, "unit")

        if not code or not name or not unit:
            raise ValueError(f"Material row is missing code, name or unit: {row}")

        materials[code] = {
            "code": code,
            "name": name,
            "lhv": lhv,
            "density": density,
            "unit": unit,
        }
        material_tags[code] = {tag_type: (cell(row, tag_type) or "").split() for tag_type in tag_columns}

with transaction.atomic():
    bulk_update_or_create(Material, "code", list(materials.values()))
    sync_tags(material_tags, tag_columns)
