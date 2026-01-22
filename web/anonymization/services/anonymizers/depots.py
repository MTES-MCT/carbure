from faker import Faker

from transactions.models import Depot

from ..utils import anonymize_fields_and_collect_modifications, get_french_coordinates
from .base import Anonymizer


class DepotAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return Depot

    def get_queryset(self):
        return Depot.objects.all()

    def get_updated_fields(self):
        return [
            "name",
            "city",
            "address",
            "postal_code",
            "gps_coordinates",
            "customs_id",
        ]

    def process(self, depot):
        fields_to_anonymize = {
            "name": f"Dépôt {depot.depot_type} {depot.id}",
            "city": self.fake.city(),
            "address": self.fake.address(),
            "postal_code": self.fake.postcode(),
            "gps_coordinates": get_french_coordinates(),
            "customs_id": self.fake.bothify(text="CUST-####"),
        }

        return anonymize_fields_and_collect_modifications(depot, fields_to_anonymize)

    def get_display_name(self):
        return "dépôts"

    def get_emoji(self):
        return "🏪"
