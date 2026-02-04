import os

import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Entity, EntityCertificate, GenericCertificate, Pays  # noqa: E402

data = {
    "operators": [
        {"registration_id": "123456780", "name": "CARBURE1"},
        {"registration_id": "123456781", "name": "CARBURE2"},
    ],
    "producers": [
        {
            "registration_id": "123456789",
            "name": "CARBURE",
            "certificate": {"id": "EU-ISCC-Cert-Test-FR004", "valid_from": "2025-08-01", "valid_until": "2026-08-01"},
        },
        {
            "registration_id": "000000011",
            "name": "CARBURE_FR_FAME_PRODUCER",
            "certificate": {"id": "EU-ISCC-Cert-FR999-00000011", "valid_from": "2026-01-08", "valid_until": "2028-01-08"},
        },
    ],
}

if settings.WITH_UDB_ACCEPTANCE_DATA:
    france = Pays.objects.get(code_pays="FR")

    def add_operator(registration_id, name):
        Entity.objects.update_or_create(
            registered_country=france,
            registration_id=registration_id,
            defaults={"entity_type": Entity.OPERATOR, "name": name},
        )

    def add_producer(producer_data):
        entity, _ = Entity.objects.update_or_create(
            registered_country=france,
            registration_id=producer_data["registration_id"],
            defaults={"entity_type": Entity.PRODUCER, "name": producer_data["name"]},
        )

        certificate_data = producer_data["certificate"]
        certificate, _ = GenericCertificate.objects.update_or_create(
            certificate_id=certificate_data["id"],
            defaults={
                "certificate_type": GenericCertificate.ISCC,
                "certificate_holder": producer_data["name"],
                "valid_from": certificate_data["valid_from"],
                "valid_until": certificate_data["valid_until"],
            },
        )

        EntityCertificate.objects.update_or_create(
            certificate=certificate,
            entity=entity,
            defaults={"checked_by_admin": True},
        )

    print("Seeding UDB acceptance data…")

    for o in data["operators"]:
        add_operator(o["registration_id"], o["name"])

    for p in data["producers"]:
        add_producer(p)
