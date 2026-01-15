import os

import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Entity, EntityCertificate, GenericCertificate, Pays  # noqa: E402

if settings.WITH_UDB_ACCEPTANCE_DATA:
    print("Seeding UDB acceptance data…")

    france = Pays.objects.get(code_pays="FR")

    carbure, _ = Entity.objects.update_or_create(
        registered_country=france,
        registration_id="123456789",
        defaults={"entity_type": Entity.PRODUCER, "name": "CARBURE"},
    )

    Entity.objects.update_or_create(
        registered_country=france,
        registration_id="123456780",
        defaults={"entity_type": Entity.OPERATOR, "name": "CARBURE1"},
    )

    certificate, _ = GenericCertificate.objects.update_or_create(
        certificate_id="EU-ISCC-Cert-Test-FR004",
        defaults={
            "certificate_type": GenericCertificate.ISCC,
            "certificate_holder": "CARBURE",
            "valid_from": "2025-08-01",
            "valid_until": "2026-08-01",
        },
    )

    EntityCertificate.objects.update_or_create(
        certificate=certificate,
        entity=carbure,
        defaults={"checked_by_admin": True},
    )
