"""
Anonymiseur spécialisé pour les entités (Entity).
"""

from faker import Faker

from core.models import Entity

from .base import Anonymizer
from .utils import anonymize_fields_and_collect_modifications


class EntityAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return Entity

    def get_queryset(self):
        return Entity.objects.filter(id=1)

    def get_updated_fields(self):
        return [
            "name",
            "legal_name",
            "sustainability_officer",
            "sustainability_officer_email",
            "sustainability_officer_phone_number",
            "registered_address",
            "registered_city",
            "registered_zipcode",
            "registration_id",
            "vat_number",
            "accise_number",
            "website",
            "activity_description",
        ]

    def process(self, entity):
        fields_to_anonymize = {
            "name": f"{entity.entity_type} - {entity.id}",
            "legal_name": f"Entity {entity.id} SA",
            "sustainability_officer": self.fake.name(),
            "sustainability_officer_email": f"contact{entity.id}@anonymized.local",
            "sustainability_officer_phone_number": self.fake.phone_number(),
            "registered_address": self.fake.address(),
            "registered_city": self.fake.city(),
            "registered_zipcode": self.fake.postcode(),
            "registration_id": self.fake.bothify(text="##########"),
            "vat_number": self.fake.bothify(text="FR#############"),
            "accise_number": self.fake.bothify(text="##########"),
            "website": self.fake.url(),
            "activity_description": "Activity description",
        }

        return anonymize_fields_and_collect_modifications(entity, fields_to_anonymize)

    def get_display_name(self):
        return "entités"

    def get_emoji(self):
        return "🏢"
