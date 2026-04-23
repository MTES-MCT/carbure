import csv

from django.contrib.contenttypes.models import ContentType

from core.models import Department, Entity, ExternalAdminRights
from entity.models import EntityScope


def load_external_admin_entities(csv_filename: str, external_admin_right: str, admin_label: str) -> None:
    dept_ct = ContentType.objects.get_for_model(Department)

    with open(csv_filename) as csvfile:
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
                print(f"Department with code {code_dept} does not exist. Skipping {admin_label} {entity_name}.")
                continue

            entity, _ = Entity.objects.get_or_create(
                name=entity_name,
                entity_type=Entity.EXTERNAL_ADMIN,
            )

            ExternalAdminRights.objects.get_or_create(
                entity=entity,
                right=external_admin_right,
            )

            EntityScope.objects.get_or_create(
                entity=entity,
                content_type=dept_ct,
                object_id=department.id,
            )
