import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.contrib.contenttypes.models import ContentType  # noqa: E402

from core.models import Department, Entity, ExternalAdminRights  # noqa: E402
from entity.models import EntityScope  # noqa: E402

filename = "%s/web/fixtures/csv/biomethane_DREAL.csv" % (os.environ["CARBURE_HOME"])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    for row in reader:
        entity_name = row[0]
        if entity_name == "name":
            # header
            continue

        code_dept = row[1]

        try:
            department = Department.objects.get(code_dept=code_dept)
        except Department.DoesNotExist:
            print(f"Department with code {code_dept} does not exist. Skipping DREAL {entity_name}.")
            continue

        # 1. Get or create DREAL entity
        entity, created = Entity.objects.get_or_create(
            name=entity_name,
            entity_type=Entity.EXTERNAL_ADMIN,
        )

        # 2. Get or create DREAL ExternalAdminRights
        dreal_external_admin_right, created = ExternalAdminRights.objects.get_or_create(
            entity=entity,
            right=ExternalAdminRights.DREAL,
        )

        # 3. Link DREAL to the department using EntityScope
        dept_ct = ContentType.objects.get_for_model(Department)
        scope, created = EntityScope.objects.get_or_create(
            entity=entity,
            content_type=dept_ct,
            object_id=department.id,
        )
