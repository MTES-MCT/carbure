from faker import Faker

from biomethane.models import BiomethaneInjectionSite

from ...utils import anonymize_fields_and_collect_modifications
from ..base import Anonymizer


class BiomethaneInjectionSiteAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return BiomethaneInjectionSite

    def get_queryset(self):
        return BiomethaneInjectionSite.objects.all()

    def get_updated_fields(self):
        return [
            "unique_identification_number",
            "meter_number",
            "company_address",
            "city",
            "postal_code",
            "network_manager_name",
        ]

    def process(self, injection_site):
        fields_to_anonymize = {
            "unique_identification_number": self.fake.bothify(text="INJ-####-####"),
            "meter_number": self.fake.bothify(text="METER-####"),
            "company_address": self.fake.address(),
            "city": self.fake.city(),
            "postal_code": self.fake.postcode(),
            "network_manager_name": self.fake.company(),
        }

        return anonymize_fields_and_collect_modifications(injection_site, fields_to_anonymize)

    def get_display_name(self):
        return "sites d'injection biométhane"

    def get_emoji(self):
        return "💉"
