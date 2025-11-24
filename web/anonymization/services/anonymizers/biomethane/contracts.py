from faker import Faker

from biomethane.models import BiomethaneContract

from ...utils import anonymize_fields_and_collect_modifications
from ..base import Anonymizer


class BiomethaneContractAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return BiomethaneContract

    def get_queryset(self):
        return BiomethaneContract.objects.all()

    def get_updated_fields(self):
        return [
            "general_conditions_file",
            "specific_conditions_file",
        ]

    def process(self, contract):
        return anonymize_fields_and_collect_modifications(
            contract,
            {
                "general_conditions_file": "fake-file.txt",
                "specific_conditions_file": "fake-file.txt",
            },
        )

    def get_display_name(self):
        return "contrats biométhane"

    def get_emoji(self):
        return "📄"
