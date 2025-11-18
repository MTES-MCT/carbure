"""
Specialized anonymizer for charge points (ElecChargePoint).
"""

from faker import Faker

from elec.models import ElecChargePoint

from ..base import Anonymizer
from ..utils import anonymize_fields_and_collect_modifications, get_french_coordinates


class ElecChargePointAnonymizer(Anonymizer):
    def __init__(self, fake: Faker):
        self.fake = fake

    def get_model(self):
        return ElecChargePoint

    def get_queryset(self):
        return ElecChargePoint.objects.prefetch_related("cpo").all()

    def get_updated_fields(self):
        return [
            "charge_point_id",
            "measure_reference_point_id",
            "station_name",
            "station_id",
            "cpo_name",
            "cpo_siren",
            "latitude",
            "longitude",
        ]

    def process(self, charge_point):
        # Parse GPS coordinates from get_french_coordinates()
        coords = get_french_coordinates()
        lat, lon = map(float, coords.split(", "))

        fields_to_anonymize = {
            "charge_point_id": self.fake.bothify(text="CP-####-####"),
            "measure_reference_point_id": self.fake.bothify(text="MRP-####"),
            "station_name": f"Station {charge_point.id}",
            "station_id": self.fake.bothify(text="ST-####"),
            "cpo_name": charge_point.cpo.name,
            "cpo_siren": charge_point.cpo.registration_id,
            "latitude": lat,
            "longitude": lon,
        }

        return anonymize_fields_and_collect_modifications(charge_point, fields_to_anonymize)

    def get_display_name(self):
        return "charge points"

    def get_emoji(self):
        return "🔌"
