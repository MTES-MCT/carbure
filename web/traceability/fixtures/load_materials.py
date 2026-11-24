import csv
import os

import django
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.utils import bulk_update_or_create  # noqa: E402
from feedstocks.models import Classification  # noqa: E402
from traceability.models import Material, MaterialTag  # noqa: E402
from traceability.models.material_tag import Tag  # noqa: E402

filename = "%s/web/traceability/fixtures/materials.csv" % (os.environ["CARBURE_HOME"])


def cell(row, column):
    """Return None for empty or missing cells."""
    return (row.get(column) or "").strip() or None


def read_materials(filename):
    materials = {}
    material_tags = {}

    with open(filename, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        columns = set(reader.fieldnames or ())
        tag_columns = columns & set(Tag.values)

        for row in reader:
            code = cell(row, "code")
            name = cell(row, "name")
            unit = cell(row, "unit")
            if not code or not name or not unit:
                raise ValueError(f"Material row is missing code, name or unit: {row}")

            materials[code] = {
                "code": code,
                "name": name,
                "unit": unit,
                "description": cell(row, "description") or "",
                "lhv": cell(row, "lhv"),
                "density": cell(row, "density"),
            }
            if "category" in columns:
                materials[code]["category"] = cell(row, "category")
            material_tags[code] = {tag_type: (cell(row, tag_type) or "").split() for tag_type in tag_columns}

    return materials, material_tags, tag_columns


def resolve_classifications(materials):
    categories = {material["category"] for material in materials.values() if material.get("category")}
    classifications = {
        category: Classification.objects.get_or_create(group="", category=category, subcategory="")[0]
        for category in categories
    }
    for material in materials.values():
        if "category" in material:
            material["classification"] = classifications.get(material.pop("category"))


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


materials, material_tags, tag_columns = read_materials(filename)

with transaction.atomic():
    resolve_classifications(materials)
    bulk_update_or_create(Material, "code", list(materials.values()))
    sync_tags(material_tags, tag_columns)
