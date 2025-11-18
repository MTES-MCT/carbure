"""
Specialized anonymizer for transfer certificates (ElecTransferCertificate).
"""

from faker import Faker

from elec.models import ElecTransferCertificate

from ..base import Anonymizer
from ..utils import anonymize_fields_and_collect_modifications


class ElecTransferCertificateAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return ElecTransferCertificate

    def get_queryset(self):
        return ElecTransferCertificate.objects.all()

    def get_updated_fields(self):
        return [
            "certificate_id",
        ]

    def process(self, certificate):
        fields_to_anonymize = {
            "certificate_id": self.fake.bothify(text="ETC-####-####"),
        }

        return anonymize_fields_and_collect_modifications(certificate, fields_to_anonymize)

    def get_display_name(self):
        return "transfer certificates"

    def get_emoji(self):
        return "📜"
