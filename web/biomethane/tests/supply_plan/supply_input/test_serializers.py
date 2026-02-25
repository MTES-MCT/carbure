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
        self.seigle_cive = MatierePremiere.objects.create(
            name="Seigle - CIVE",
            name_en="Rye - CIVE",
            code="Seigle - CIVE",
            is_methanogenic=True,
        )
        self.autres_cultures = MatierePremiere.objects.create(
            name="Autres cultures",
            name_en="Other crops",
            code="Autres cultures",
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
            "average_weighted_distance_km": 50.0,
            "maximum_distance_km": 100.0,
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

    def test_validate_france_requires_fields(self):
        """Test origin_country=FR requires average_weighted_distance_km, maximum_distance_km and origin_department."""
        required_fields = [
            "average_weighted_distance_km",
            "maximum_distance_km",
            "origin_department",
        ]
        for field in required_fields:
            with self.subTest(field=field):
                data = {**self.valid_data, field: None}
                serializer = BiomethaneSupplyInputCreateSerializer(data=data)
                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)
                self.assertIn("Ce champ est requis pour la France", str(serializer.errors[field]))

    def test_validate_seigle_cive_requires_type_cive(self):
        """Test input_name 'Seigle - CIVE' requires type_cive (SUMMER or WINTER)."""
        data = {
            **self.valid_data,
            "input_name": "Seigle - CIVE",
            "type_cive": None,
        }
        serializer = BiomethaneSupplyInputCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("type_cive", serializer.errors)

    def test_validate_seigle_cive_valid_with_type_cive(self):
        """Test input_name 'Seigle - CIVE' is valid with type_cive SUMMER or WINTER."""
        for type_cive in (BiomethaneSupplyInput.SUMMER, BiomethaneSupplyInput.WINTER):
            with self.subTest(type_cive=type_cive):
                data = {
                    **self.valid_data,
                    "input_name": "Seigle - CIVE",
                    "type_cive": type_cive,
                }
                serializer = BiomethaneSupplyInputCreateSerializer(data=data)
                self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_other_input_clears_type_cive(self):
        """Test when input_name is not Seigle - CIVE, type_cive is set to None."""
        data = {
            **self.valid_data,
            "input_name": "Maïs",
            "type_cive": BiomethaneSupplyInput.SUMMER,
        }
        serializer = BiomethaneSupplyInputCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data["type_cive"])

    def test_validate_autres_cultures_requires_culture_details(self):
        """Test input_name 'Autres cultures' requires culture_details."""
        data = {
            **self.valid_data,
            "input_name": "Autres cultures",
            "culture_details": None,
        }
        serializer = BiomethaneSupplyInputCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("culture_details", serializer.errors)

    def test_validate_autres_cultures_valid_with_culture_details(self):
        """Test input_name 'Autres cultures' is valid with culture_details filled."""
        data = {
            **self.valid_data,
            "input_name": "Autres cultures",
            "culture_details": "Mélange céréales",
        }
        serializer = BiomethaneSupplyInputCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["culture_details"], "Mélange céréales")

    def test_validate_other_input_clears_culture_details(self):
        """Test when input_name is not Autres cultures, culture_details is set to None."""
        data = {
            **self.valid_data,
            "input_name": "Maïs",
            "culture_details": "Some details",
        }
        serializer = BiomethaneSupplyInputCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data["culture_details"])
