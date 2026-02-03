from faker import Faker

from core.models import CarbureLotComment

from ..utils import anonymize_fields_and_collect_modifications
from .base import Anonymizer


class CarbureLotCommentAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return CarbureLotComment

    def get_queryset(self):
        return CarbureLotComment.objects.all()

    def get_updated_fields(self):
        return [
            "comment",
        ]

    def process(self, comment):
        fields_to_anonymize = {
            "comment": self.fake.text(max_nb_chars=500),
        }

        return anonymize_fields_and_collect_modifications(comment, fields_to_anonymize)

    def get_display_name(self):
        return "carbure lot comments"

    def get_emoji(self):
        return "💬"
