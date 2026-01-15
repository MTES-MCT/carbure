from faker import Faker

from saf.models import SafTicketSource

from ...utils import anonymize_fields_and_collect_modifications
from ..base import Anonymizer


class SafTicketSourceAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return SafTicketSource

    def get_queryset(self):
        return SafTicketSource.objects.all()

    def get_updated_fields(self):
        return [
            "carbure_id",
            "unknown_producer",
            "unknown_production_site",
        ]

    def process(self, ticket_source):
        fields_to_anonymize = {
            "carbure_id": self.fake.bothify(text="TS####-##-####"),
            "unknown_producer": self.fake.company(),
            "unknown_production_site": self.fake.bothify(text="SITE-####"),
        }

        return anonymize_fields_and_collect_modifications(ticket_source, fields_to_anonymize)

    def get_display_name(self):
        return "SAF ticket sources"

    def get_emoji(self):
        return "📋"
