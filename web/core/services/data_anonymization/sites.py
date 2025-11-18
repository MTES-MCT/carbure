"""
Anonymiseur spécialisé pour les sites (Site).
"""

from faker import Faker

from transactions.models import Site

from .base import Anonymizer
from .utils import anonymize_fields_and_collect_modifications, get_french_coordinates


class SiteAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return Site

    def get_queryset(self):
        return Site.objects.all()

    def get_updated_fields(self):
        return [
            "name",
            "site_siret",
            "customs_id",
            "address",
            "postal_code",
            "city",
            "gps_coordinates",
            "dc_number",
            "manager_name",
            "manager_phone",
            "manager_email",
            "icao_code",
        ]

    def process(self, site):
        fields_to_anonymize = {
            "name": f"Site {site.site_type} {site.id}",
            "site_siret": self.fake.bothify(text="##############"),
            "customs_id": self.fake.bothify(text="CUST-####"),
            "address": self.fake.address(),
            "postal_code": self.fake.postcode(),
            "city": self.fake.city(),
            "gps_coordinates": get_french_coordinates(),
            "dc_number": self.fake.bothify(text="DC-####") if site.eligible_dc else None,
            "dc_reference": self.fake.bothify(text="DC-REF-####") if site.eligible_dc else None,
            "manager_name": self.fake.name(),
            "manager_phone": self.fake.phone_number(),
            "manager_email": f"manager{site.id}@anonymized.local",
            "icao_code": self.fake.bothify(text="????").upper(),
        }

        return anonymize_fields_and_collect_modifications(site, fields_to_anonymize)

    def get_display_name(self):
        return "sites"

    def get_emoji(self):
        return "📍"
