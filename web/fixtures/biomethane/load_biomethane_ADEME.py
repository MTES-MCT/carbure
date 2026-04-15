import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.contrib.contenttypes.models import ContentType  # noqa: E402
from load_biomethane_utils import load_external_admin_entities  # noqa: E402

from core.models import ExternalAdminRights  # noqa: E402
from core.models.entity import Entity  # noqa: E402
from core.models.geography import Department  # noqa: E402
from entity.models import EntityScope  # noqa: E402

filename = "%s/web/fixtures/csv/biomethane_ADEME.csv" % (os.environ["CARBURE_HOME"])
load_external_admin_entities(filename, ExternalAdminRights.ADEME, "ADEME")

# Create national entity for ADEME
entity, created = Entity.objects.get_or_create(
    name="ADEME",
    entity_type=Entity.EXTERNAL_ADMIN,
)

# If the entity is created, add the ADEME right and the departments scopes
if created:
    ExternalAdminRights.objects.get_or_create(
        entity=entity,
        right=ExternalAdminRights.ADEME,
    )

    all_departments = Department.objects.all()
    for department in all_departments:
        EntityScope.objects.get_or_create(
            entity=entity,
            content_type=ContentType.objects.get_for_model(Department),
            object_id=department.id,
        )
