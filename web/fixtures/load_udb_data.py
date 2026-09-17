import os

import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Entity, EntityCertificate, GenericCertificate, Pays  # noqa: E402
from transactions.models.entity_site import EntitySite  # noqa: E402
from transactions.models.site import Site  # noqa: E402

data = {
    "operators": [
        {"registration_id": "123456780", "name": "CARBURE1"},
        {"registration_id": "123456781", "name": "CARBURE2"},
    ],
    "producers": [
        {
            "registration_id": "123456789",
            "name": "CARBURE",
            "registered_address": "12 rue des Affiches",
            "registered_zipcode": "13000",
            "registered_city": "Marseille",
            "sites": [],
            "certificate": {
                "id": "EU-ISCC-Cert-Test-FR004",
                "type": GenericCertificate.ISCC,
                "issuer": "",
                "valid_from": "2025-08-01",
                "valid_until": "2026-08-01",
            },
        },
        {
            "registration_id": "000000011",
            "name": "CARBURE_FR_FAME_PRODUCER",
            "registered_address": "11bis boulevard du Siège Social",
            "registered_zipcode": "75001",
            "registered_city": "Paris",
            "sites": [],
            "certificate": {
                "id": "EU-ISCC-Cert-FR999-00000011",
                "type": GenericCertificate.ISCC,
                "issuer": "",
                "valid_from": "2026-01-08",
                "valid_until": "2028-01-08",
            },
        },
        {
            "registration_id": "000004807",
            "name": "CARBURE_EO_THROUGH_API",
            "registered_address": "1 boulevard du Siège Social",
            "registered_zipcode": "75001",
            "registered_city": "Paris",
            "sites": [
                {
                    "name": "Some Site",
                    "address": "1 rue du Chat-Perché",
                    "postal_code": "75010",
                    "city": "Paris",
                },
            ],
            "certificate": {
                "id": "SN_UN_2026_0179",
                "type": GenericCertificate.SYSTEME_NATIONAL,
                "issuer": "Control Union",
                "valid_from": "2026-01-08",
                "valid_until": "2028-01-08",
            },
        },
        {
            "registration_id": "000001789",
            "name": "ANOTHER_CARBURE_EO_THROUGH_API",
            "registered_address": "1 rue du site principal",
            "registered_zipcode": "69000",
            "registered_city": "Lyon",
            "sites": [
                {
                    "name": "Some Site",
                    "address": "1 impasse des Planches",
                    "postal_code": "69100",
                    "city": "Villeurbanne",
                },
            ],
            "certificate": {
                "id": "SN_UN_2026_1789",
                "type": GenericCertificate.SYSTEME_NATIONAL,
                "issuer": "Control Union",
                "valid_from": "2026-01-08",
                "valid_until": "2028-01-08",
            },
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
            defaults={
                "entity_type": Entity.PRODUCER,
                "name": producer_data["name"],
                "registered_address": producer_data.get("registered_address", ""),
                "registered_zipcode": producer_data.get("registered_zipcode", ""),
                "registered_city": producer_data.get("registered_city", ""),
            },
        )

        certificate_data = producer_data["certificate"]
        certificate, _ = GenericCertificate.objects.update_or_create(
            certificate_id=certificate_data["id"],
            certificate_type=certificate_data["type"],
            defaults={
                "certificate_holder": producer_data["name"],
                "certificate_issuer": certificate_data["issuer"],
                "scope": "FSP, PB",
                "status": GenericCertificate.VALID,
                "valid_from": certificate_data["valid_from"],
                "valid_until": certificate_data["valid_until"],
                "last_status_update": certificate_data["valid_from"],
            },
        )

        sites_data = producer_data["sites"]
        for s in sites_data:
            site, _ = Site.objects.update_or_create(**s, defaults={"country": france})
            EntitySite.objects.update_or_create(entity=entity, site=site)

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
