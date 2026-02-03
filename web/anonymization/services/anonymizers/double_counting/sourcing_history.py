from faker import Faker

from doublecount.models import DoubleCountingSourcingHistory

from ...utils import anonymize_fields_and_collect_modifications
from ..base import Anonymizer


class DoubleCountingSourcingHistoryAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return DoubleCountingSourcingHistory

    def get_queryset(self):
        return DoubleCountingSourcingHistory.objects.all()

    def get_updated_fields(self):
        return [
            "raw_material_supplier",
            "supplier_certificate_name",
        ]

    def process(self, sourcing_history):
        fields_to_anonymize = {
            "raw_material_supplier": self.fake.word(),
            "supplier_certificate_name": self.fake.bothify(text="CERT-####-####"),
        }

        return anonymize_fields_and_collect_modifications(sourcing_history, fields_to_anonymize)

    def get_display_name(self):
        return "historique d'approvisionnement double comptage"

    def get_emoji(self):
        return "📊"
