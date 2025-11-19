"""
Specialized anonymizer for Carbure lots (CarbureLot).
"""

from faker import Faker

from core.models import CarbureLot

from .base import Anonymizer
from .utils import anonymize_fields_and_collect_modifications


class CarbureLotAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return CarbureLot

    def get_queryset(self):
        # Utiliser only() pour limiter les colonnes chargées depuis la base de données
        # On inclut 'id' (clé primaire nécessaire pour bulk_update) et tous les champs à mettre à jour
        fields_to_load = ["id"] + self.get_updated_fields()
        return CarbureLot.objects.only(*fields_to_load)[:6000]

    def get_updated_fields(self):
        return [
            "carbure_id",
            "unknown_producer",
            "unknown_production_site",
            "unknown_supplier",
            "unknown_client",
            "unknown_dispatch_site",
            "unknown_delivery_site",
            "production_site_certificate",
            "production_site_certificate_type",
            "production_site_double_counting_certificate",
            "supplier_certificate",
            "supplier_certificate_type",
            "vendor_certificate",
            "vendor_certificate_type",
            "transport_document_reference",
            "free_field",
        ]

    def process(self, lot):
        fields_to_anonymize = {
            "carbure_id": self.fake.bothify(text="LOT-####-####"),
            "unknown_producer": self.fake.company(),
            "unknown_production_site": self.fake.bothify(text="SITE-####"),
            "unknown_supplier": self.fake.company(),
            "unknown_client": self.fake.company(),
            "unknown_dispatch_site": self.fake.bothify(text="DISPATCH-SITE-####"),
            "unknown_delivery_site": self.fake.bothify(text="DELIVERY-SITE-####"),
            "production_site_certificate": self.fake.bothify(text="CERT-####-####"),
            "production_site_certificate_type": self.fake.bothify(text="CERT-TYPE-####"),
            "production_site_double_counting_certificate": self.fake.bothify(text="DC-CERT-####"),
            "supplier_certificate": self.fake.bothify(text="SUP-CERT-####"),
            "supplier_certificate_type": self.fake.bothify(text="SUP-TYPE-####"),
            "vendor_certificate": self.fake.bothify(text="VEN-CERT-####"),
            "vendor_certificate_type": self.fake.bothify(text="VEN-TYPE-####"),
            "transport_document_reference": self.fake.bothify(text="DOC-####-####"),
            "free_field": self.fake.text(max_nb_chars=200),
        }

        return anonymize_fields_and_collect_modifications(lot, fields_to_anonymize)

    def get_display_name(self):
        return "Lots de biocarburant"

    def get_emoji(self):
        return "📦"
