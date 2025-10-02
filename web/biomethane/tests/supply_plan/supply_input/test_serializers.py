from django.test import TestCase

from biomethane.models import BiomethaneSupplyInput
from biomethane.serializers import BiomethaneSupplyInputCreateSerializer


class BiomethaneSupplyInputSerializerTests(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.valid_data = {
            "material_unit": BiomethaneSupplyInput.WET,
            "dry_matter_ratio_percent": None,
            "source": BiomethaneSupplyInput.INTERNAL,
            "crop_type": BiomethaneSupplyInput.MAIN,
            "input_category": BiomethaneSupplyInput.CIVE,
            "input_type": "Maïs",
            "volume": 1000.0,
            "origin_country": 77,
            "origin_department": "75",
        }

    def test_validate_dry_material_requires_ratio(self):
        """Test material_unit=DRY requires dry_matter_ratio_percent."""
        valid_data = {
            **self.valid_data,
            "material_unit": BiomethaneSupplyInput.DRY,
            "dry_matter_ratio_percent": None,
        }

        serializer = BiomethaneSupplyInputCreateSerializer(data=valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("dry_matter_ratio_percent", serializer.errors)

    def test_validate_wet_material_forbids_ratio(self):
        """Test material_unit=WET forbids dry_matter_ratio_percent."""
        valid_data = {
            **self.valid_data,
            "material_unit": BiomethaneSupplyInput.WET,
            "dry_matter_ratio_percent": 85.0,
        }

        serializer = BiomethaneSupplyInputCreateSerializer(data=valid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("dry_matter_ratio_percent", serializer.errors)
