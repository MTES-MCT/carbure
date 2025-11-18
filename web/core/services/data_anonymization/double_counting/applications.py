"""
Anonymiseur spécialisé pour les dossiers double compte (DoubleCountingApplication).
"""

from faker import Faker

from doublecount.models import DoubleCountingApplication

from ..base import Anonymizer
from ..utils import anonymize_fields_and_collect_modifications


class DoubleCountingApplicationAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return DoubleCountingApplication

    def get_queryset(self):
        return DoubleCountingApplication.objects.all()

    def get_updated_fields(self):
        return [
            "download_link",
        ]

    def process(self, application):
        fields_to_anonymize = {"download_link": "fake_file.txt"}

        return anonymize_fields_and_collect_modifications(application, fields_to_anonymize)

    def get_display_name(self):
        return "dossiers double comptage"

    def get_emoji(self):
        return "📋"
