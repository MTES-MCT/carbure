import csv
import os
from pathlib import Path

import django
from django.db import transaction

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
    django.setup()

from core.utils import bulk_update_or_create  # noqa: E402
from feedstocks.models import Classification  # noqa: E402
from traceability.models import Material, MaterialTag  # noqa: E402
from traceability.models.material_tag import Tag  # noqa: E402

REQUIRED_COLUMNS = {"code", "name", "unit"}


def read_catalog(filename):
    catalog = {}
    with open(filename, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        columns = set(reader.fieldnames or ())
        if not REQUIRED_COLUMNS <= columns:
            raise ValueError("Material CSV must have code, name and unit columns")

        for raw_row in reader:
            row = {column: (raw_row[column] or "").strip() for column in columns}
            if not all(row[column] for column in REQUIRED_COLUMNS):
                raise ValueError(f"Material row is missing code, name or unit: {raw_row}")
            catalog[row["code"]] = row

    return catalog, columns


def sync_materials(catalog):
    categories = {row["category"] for row in catalog.values() if row.get("category")}
    classifications = {
        category: Classification.objects.get_or_create(group="", category=category, subcategory="")[0]
        for category in categories
    }

    materials = []
    for code, row in catalog.items():
        material = {
            "code": code,
            "name": row["name"],
            "unit": row["unit"],
            "description": row.get("description", ""),
            "lhv": row.get("lhv") or None,
            "density": row.get("density") or None,
            "is_active": True,
        }
        if "category" in row:
            material["classification"] = classifications.get(row["category"])
        materials.append(material)

    bulk_update_or_create(Material, "code", materials)
    Material.active.exclude(code__in=catalog).update(is_active=False)


def sync_tags(catalog, columns):
    tag_columns = columns & set(Tag.values)
    if not catalog or not tag_columns:
        return

    material_ids = dict(Material.objects.filter(code__in=catalog).values_list("code", "pk"))
    tags_to_create = {
        (material_ids[code], tag_type, value)
        for code, row in catalog.items()
        for tag_type in tag_columns
        for value in row[tag_type].split()
    }

    existing_tags = MaterialTag.objects.filter(material_id__in=material_ids.values(), type__in=tag_columns).order_by("pk")
    obsolete_ids = []
    for tag in existing_tags:
        key = (tag.material_id, tag.type, tag.value)
        if key in tags_to_create:
            tags_to_create.remove(key)
        else:
            obsolete_ids.append(tag.pk)

    MaterialTag.objects.filter(pk__in=obsolete_ids).delete()
    MaterialTag.objects.bulk_create(
        [MaterialTag(material_id=material_id, type=tag_type, value=value) for material_id, tag_type, value in tags_to_create]
    )


def load_materials(filename=None):
    if filename is None:
        carbure_home = os.environ.get("CARBURE_HOME")
        filename = (
            Path(carbure_home) / "web/traceability/fixtures/materials.csv"
            if carbure_home
            else Path(__file__).with_name("materials.csv")
        )

    catalog, columns = read_catalog(filename)

    with transaction.atomic():
        sync_materials(catalog)
        sync_tags(catalog, columns)


if __name__ == "__main__":
    load_materials()
