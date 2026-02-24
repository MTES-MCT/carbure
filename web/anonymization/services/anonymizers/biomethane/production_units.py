from faker import Faker

from biomethane.models import BiomethaneProductionUnit

from ...utils import anonymize_fields_and_collect_modifications
from ..base import Anonymizer


class BiomethaneProductionUnitAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return BiomethaneProductionUnit

    def get_queryset(self):
        return BiomethaneProductionUnit.objects.all()

    def get_updated_fields(self):
        return [
            "name",
            "site_siret",
            "address",
            "city",
            "postal_code",
        ]

    def process(self, production_unit):
        fields_to_anonymize = {
            "name": f"Unité de Production {production_unit.id}",
            "site_siret": self.fake.bothify(text="##############"),
            "address": self.fake.address(),
            "city": self.fake.city(),
            "postal_code": self.fake.postcode(),
        }

        return anonymize_fields_and_collect_modifications(production_unit, fields_to_anonymize)

    def get_display_name(self):
        return "unités de production biométhane"

    def get_emoji(self):
        return "⚙️"
