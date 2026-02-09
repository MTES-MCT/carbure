import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import Entity, ExternalAdminRights  # noqa: E402

filename = "%s/web/fixtures/csv/DGDDI.csv" % (os.environ["CARBURE_HOME"])


def rename_entity(name):
    if "bureau" in name:
        name = name.replace("bureau", "").strip()

    return f"Bureau DGDDI - {name}"


with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    for row in reader:
        entity_name = row[0]
        if entity_name == "name":
            # header
            continue

        new_name = rename_entity(entity_name)

        # 1. Get or create DGDDI entity
        entity, created = Entity.objects.get_or_create(
            name=new_name,
            entity_type=Entity.EXTERNAL_ADMIN,
        )

        # 2. Get or create DGDDI ExternalAdminRights
        dreal_external_admin_right, created = ExternalAdminRights.objects.get_or_create(
            entity=entity,
            right=ExternalAdminRights.DGDDI,
        )

        print(f"Processed entity: {entity.name}")
