"""
Specialized anonymizer for electric meters (ElecMeter).
"""

from faker import Faker

from elec.models import ElecMeter

from ..base import Anonymizer
from ..utils import anonymize_fields_and_collect_modifications


class ElecMeterAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return ElecMeter

    def get_queryset(self):
        return ElecMeter.objects.all()

    def get_updated_fields(self):
        return [
            "mid_certificate",
        ]

    def process(self, meter):
        fields_to_anonymize = {
            "mid_certificate": self.fake.bothify(text="MID-CERT-####-####"),
        }

        return anonymize_fields_and_collect_modifications(meter, fields_to_anonymize)

    def get_display_name(self):
        return "MID meters"

    def get_emoji(self):
        return "📊"
