from faker import Faker

from elec.models import ElecProvisionCertificateQualicharge

from ...utils import anonymize_fields_and_collect_modifications
from ..base import Anonymizer


class ElecProvisionCertificateQualichargeAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return ElecProvisionCertificateQualicharge

    def get_queryset(self):
        return ElecProvisionCertificateQualicharge.objects.all()

    def get_updated_fields(self):
        return [
            "operating_unit",
            "station_id",
        ]

    def process(self, certificate):
        fields_to_anonymize = {}

        if certificate.operating_unit:
            fields_to_anonymize["operating_unit"] = self.fake.bothify(text="OP-####")

        if certificate.station_id:
            fields_to_anonymize["station_id"] = self.fake.bothify(text="ST-####")

        return anonymize_fields_and_collect_modifications(certificate, fields_to_anonymize)

    def get_display_name(self):
        return "Certificats de fourniture Qualicharge"

    def get_emoji(self):
        return "⚡"
