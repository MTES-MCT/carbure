from faker import Faker

from transactions.models import ProductionSite

from ..utils import anonymize_fields_and_collect_modifications, get_french_coordinates
from .base import Anonymizer


class ProductionSiteAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return ProductionSite

    def get_queryset(self):
        return ProductionSite.objects.all()

    def get_updated_fields(self):
        return [
            "name",
            "address",
            "city",
            "postal_code",
            "manager_name",
            "manager_phone",
            "manager_email",
            "site_id",
            "dc_number",
            "dc_reference",
            "gps_coordinates",
        ]

    def process(self, production_site):
        fields_to_anonymize = {
            "name": f"Site de Production {production_site.id}",
            "address": self.fake.address(),
            "city": self.fake.city(),
            "postal_code": self.fake.postcode(),
            "manager_name": self.fake.name(),
            "manager_email": f"manager{production_site.id}@anonymized.local",
            "manager_phone": self.fake.phone_number(),
            "site_id": self.fake.bothify(text="SITE-####"),
            "dc_number": self.fake.bothify(text="DC-####") if production_site.eligible_dc else "",
            "dc_reference": self.fake.bothify(text="DC-REF-####") if production_site.eligible_dc else "",
            "gps_coordinates": get_french_coordinates(),
        }

        return anonymize_fields_and_collect_modifications(production_site, fields_to_anonymize)

    def get_display_name(self):
        return "sites de production"

    def get_emoji(self):
        return "🏭"
