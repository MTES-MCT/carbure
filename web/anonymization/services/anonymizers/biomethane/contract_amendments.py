from faker import Faker

from biomethane.models import BiomethaneContractAmendment

from ...utils import anonymize_fields_and_collect_modifications
from ..base import Anonymizer


class BiomethaneContractAmendmentAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return BiomethaneContractAmendment

    def get_queryset(self):
        return BiomethaneContractAmendment.objects.all()

    def get_updated_fields(self):
        return [
            "amendment_file",
            "amendment_details",
        ]

    def process(self, amendment):
        return anonymize_fields_and_collect_modifications(
            amendment,
            {
                "amendment_file": "fake-file.txt",
                "amendment_details": self.fake.text(max_nb_chars=500),
            },
        )

    def get_display_name(self):
        return "Avenants contrats biométhane"

    def get_emoji(self):
        return "📝"
