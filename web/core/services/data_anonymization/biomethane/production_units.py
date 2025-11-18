"""
Anonymiseur spécialisé pour les unités de production biométhane (BiomethaneProductionUnit).
"""

from faker import Faker

from biomethane.models import BiomethaneProductionUnit

from ..base import Anonymizer
from ..utils import anonymize_fields_and_collect_modifications


class BiomethaneProductionUnitAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return BiomethaneProductionUnit

    def get_queryset(self):
        return BiomethaneProductionUnit.objects.all()

    def get_updated_fields(self):
        return [
            "unit_name",
            "siret_number",
            "company_address",
            "city",
            "postal_code",
        ]

    def process(self, production_unit):
        fields_to_anonymize = {
            "unit_name": f"Unité de Production {production_unit.id}",
            "siret_number": self.fake.bothify(text="##############"),
            "company_address": self.fake.address(),
            "city": self.fake.city(),
            "postal_code": self.fake.postcode(),
        }

        return anonymize_fields_and_collect_modifications(production_unit, fields_to_anonymize)

    def get_display_name(self):
        return "unités de production biométhane"

    def get_emoji(self):
        return "⚙️"
