from faker import Faker

from certificates.models import DoubleCountingRegistration

from ...utils import anonymize_fields_and_collect_modifications
from ..base import Anonymizer


class DoubleCountingRegistrationAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return DoubleCountingRegistration

    def get_queryset(self):
        return DoubleCountingRegistration.objects.all()

    def get_updated_fields(self):
        return [
            "certificate_holder",
            "registered_address",
        ]

    def process(self, application):
        fields_to_anonymize = {
            "certificate_holder": self.fake.company(),
            "registered_address": self.fake.address(),
        }

        return anonymize_fields_and_collect_modifications(application, fields_to_anonymize)

    def get_display_name(self):
        return "certificats inscriptions double comptage"

    def get_emoji(self):
        return "📄"
