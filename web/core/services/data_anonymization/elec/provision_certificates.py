"""
Specialized anonymizer for provision certificates (ElecProvisionCertificate).
"""

from faker import Faker

from elec.models import ElecProvisionCertificate

from ..base import Anonymizer
from ..utils import anonymize_fields_and_collect_modifications


class ElecProvisionCertificateAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return ElecProvisionCertificate

    def get_queryset(self):
        return ElecProvisionCertificate.objects.all()

    def get_updated_fields(self):
        return [
            "operating_unit",
        ]

    def process(self, certificate):
        fields_to_anonymize = {
            "operating_unit": self.fake.bothify(text="OP-####"),
        }

        return anonymize_fields_and_collect_modifications(certificate, fields_to_anonymize)

    def get_display_name(self):
        return "provision certificates"

    def get_emoji(self):
        return "⚡"
