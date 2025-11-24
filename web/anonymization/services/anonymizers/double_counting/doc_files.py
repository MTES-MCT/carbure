from faker import Faker

from doublecount.models import DoubleCountingDocFile

from ...utils import anonymize_fields_and_collect_modifications
from ..base import Anonymizer


class DoubleCountingDocFileAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return DoubleCountingDocFile

    def get_queryset(self):
        return DoubleCountingDocFile.objects.all()

    def get_updated_fields(self):
        return [
            "url",
            "file_name",
        ]

    def process(self, doc_file):
        fields_to_anonymize = {
            "url": "fake-file.txt",
            "file_name": f"{doc_file.file_type}-fake-file.txt",
        }

        return anonymize_fields_and_collect_modifications(doc_file, fields_to_anonymize)

    def get_display_name(self):
        return "fichiers double comptage"

    def get_emoji(self):
        return "📎"
