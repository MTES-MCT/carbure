from django.test import TestCase

from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.serializers.digestate.digestate import BiomethaneDigestateInputSerializer


class BiomethaneDigestateSerializerTests(TestCase):
    def test_digestate_input_serializer_valid_data(self):
        """Test creating digestate with valid data."""
        data = {
            "raw_digestate_tonnage_produced": 2000.0,
            "raw_digestate_dry_matter_rate": 10.0,
            "solid_digestate_tonnage": 800.0,
            "liquid_digestate_quantity": 1200.0,
            "average_spreading_valorization_distance": 30.0,
            "composting_locations": [BiomethaneDigestate.ON_SITE, BiomethaneDigestate.EXTERNAL_PLATFORM],
            "on_site_composted_digestate_volume": 400.0,
            "external_platform_name": "Platform XYZ",
            "external_platform_digestate_volume": 500.0,
            "external_platform_department": "75",
            "external_platform_municipality": "Paris",
        }

        serializer = BiomethaneDigestateInputSerializer(data=data)
        self.assertTrue(serializer.is_valid())
