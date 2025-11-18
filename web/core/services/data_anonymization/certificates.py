"""
Specialized anonymizer for certificates (GenericCertificate).
"""

from faker import Faker

from core.models import GenericCertificate

from .base import Anonymizer
from .utils import anonymize_fields_and_collect_modifications


class CertificateAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return GenericCertificate

    def get_queryset(self):
        return GenericCertificate.objects.all()

    def get_updated_fields(self):
        return [
            "certificate_id",
            "certificate_holder",
            "certificate_issuer",
            "address",
            "download_link",
        ]

    def process(self, certificate):
        fields_to_anonymize = {
            "certificate_id": self.fake.bothify(text="CERT-####-####"),
            "certificate_holder": self.fake.company(),
            "certificate_issuer": self.fake.company(),
            "address": self.fake.address(),
            "download_link": self.fake.url(),
        }

        return anonymize_fields_and_collect_modifications(certificate, fields_to_anonymize)

    def get_display_name(self):
        return "certificates"

    def get_emoji(self):
        return "📜"
