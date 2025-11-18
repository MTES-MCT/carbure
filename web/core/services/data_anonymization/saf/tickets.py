"""
Specialized anonymizer for SAF tickets (SafTicket).
"""

from faker import Faker

from saf.models import SafTicket

from ..base import Anonymizer
from ..utils import anonymize_fields_and_collect_modifications


class SafTicketAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return SafTicket

    def get_queryset(self):
        return SafTicket.objects.all()

    def get_updated_fields(self):
        return [
            "carbure_id",
            "agreement_reference",
            "unknown_producer",
            "unknown_production_site",
            "free_field",
            "client_comment",
        ]

    def process(self, ticket):
        fields_to_anonymize = {
            "carbure_id": self.fake.bothify(text="T####-##-####"),
            "agreement_reference": self.fake.bothify(text="AGR-####-####"),
            "unknown_producer": self.fake.company(),
            "unknown_production_site": self.fake.bothify(text="SITE-####"),
            "free_field": self.fake.text(max_nb_chars=200),
            "client_comment": self.fake.text(max_nb_chars=200),
        }

        return anonymize_fields_and_collect_modifications(ticket, fields_to_anonymize)

    def get_display_name(self):
        return "SAF tickets"

    def get_emoji(self):
        return "✈️"
