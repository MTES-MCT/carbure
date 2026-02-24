from django.test import TestCase

from biomethane.models import BiomethaneSupplyInput
from biomethane.serializers import BiomethaneSupplyInputCreateSerializer
from core.models import MatierePremiere


class BiomethaneSupplyInputSerializerTests(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.matiere_premiere = MatierePremiere.objects.create(
            name="Maïs",
            name_en="Corn",
            code="MAIS",
            is_methanogenic=True,
        )

        self.valid_data = {
            "material_unit": BiomethaneSupplyInput.WET,
            "dry_matter_ratio_percent": None,
            "source": BiomethaneSupplyInput.INTERNAL,
            "crop_type": BiomethaneSupplyInput.MAIN,
            "input_name": "Maïs",
            "volume": 1000.0,
            "origin_country": "FR",
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

        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data["dry_matter_ratio_percent"])
