from django.test import TestCase

from biomethane.models import BiomethaneSupplyInput
from biomethane.serializers import BiomethaneSupplyInputCreateSerializer
from core.models import MatierePremiere
from feedstocks.models import Classification


class BiomethaneSupplyInputSerializerTests(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.matiere_premiere = MatierePremiere.objects.create(
            name="Maïs",
            name_en="Corn",
            code="MAIS",
            is_methanogenic=True,
        )
        # Type de CIVE: required when classification.category == "Biomasse agricole - Cultures intermédiaires"
        self.classification_cive = Classification.objects.create(
            group="Biomasse",
            category="Biomasse agricole - Cultures intermédiaires",
            subcategory="CIVE",
        )
        self.seigle_cive = MatierePremiere.objects.create(
            name="Seigle - CIVE",
            name_en="Rye - CIVE",
            code="SEIGLE_CIVE",
            is_methanogenic=True,
            classification=self.classification_cive,
        )
        # Précisez la culture: required when code is AUTRES_CULTURES or AUTRES_CULTURES_CIVE
        self.autres_cultures = MatierePremiere.objects.create(
            name="Autres cultures",
            name_en="Other crops",
            code="AUTRES_CULTURES",
            is_methanogenic=True,
        )
        self.autres_cultures_cive = MatierePremiere.objects.create(
            name="Autres cultures CIVE",
            name_en="Other crops CIVE",
            code="AUTRES_CULTURES_CIVE",
            is_methanogenic=True,
        )
        # Type de collecte: required when name is in COLLECTION_TYPE_INPUT_NAMES
        self.huiles_animale = MatierePremiere.objects.create(
            name="Huiles alimentaires usagées d'origine animale",
            name_en="Used cooking oil of animal origin",
            code="HUILES_ANIMALE",
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

    def test_validate_type_cive_required_when_classification_category_cive(self):
        """Test type_cive required when input_name has classification.category CIVE."""
        data = {
            **self.valid_data,
            "input_name": "Seigle - CIVE",
            "type_cive": None,
        }
        serializer = BiomethaneSupplyInputCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("type_cive", serializer.errors)

    def test_validate_type_cive_valid_when_classification_category_cive(self):
        """Test valid with type_cive when classification.category is CIVE."""
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
        """Test when input_name has no CIVE classification category, type_cive is set to None."""
        data = {
            **self.valid_data,
            "input_name": "Maïs",
            "type_cive": BiomethaneSupplyInput.SUMMER,
        }
        serializer = BiomethaneSupplyInputCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data["type_cive"])

    def test_validate_culture_details_required_when_code_autres_cultures(self):
        """Test culture_details required when input_name.code is AUTRES_CULTURES or AUTRES_CULTURES_CIVE."""
        for name in ("Autres cultures", "Autres cultures CIVE"):
            with self.subTest(name=name):
                data = {
                    **self.valid_data,
                    "input_name": name,
                    "culture_details": None,
                }
                serializer = BiomethaneSupplyInputCreateSerializer(data=data)
                self.assertFalse(serializer.is_valid())
                self.assertIn("culture_details", serializer.errors)

    def test_validate_culture_details_valid_when_code_autres_cultures(self):
        """Test valid with culture_details when code is AUTRES_CULTURES."""
        data = {
            **self.valid_data,
            "input_name": "Autres cultures",
            "culture_details": "Mélange céréales",
        }
        serializer = BiomethaneSupplyInputCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["culture_details"], "Mélange céréales")

    def test_validate_other_input_clears_culture_details(self):
        """Test when input_name.code is not AUTRES_CULTURES/AUTRES_CULTURES_CIVE, culture_details is None."""
        data = {
            **self.valid_data,
            "input_name": "Maïs",
            "culture_details": "Some details",
        }
        serializer = BiomethaneSupplyInputCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data["culture_details"])

    def test_validate_collection_type_required_when_name_in_list(self):
        """Test collection_type required when input_name.name is in COLLECTION_TYPE_INPUT_NAMES."""
        data = {
            **self.valid_data,
            "input_name": "Huiles alimentaires usagées d'origine animale",
            "collection_type": None,
        }
        serializer = BiomethaneSupplyInputCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("collection_type", serializer.errors)

    def test_validate_collection_type_valid_when_name_in_list(self):
        """Test valid with collection_type when input name is in the waste list."""
        for collection_type in (
            BiomethaneSupplyInput.PRIVATE,
            BiomethaneSupplyInput.LOCAL,
            BiomethaneSupplyInput.BOTH,
        ):
            with self.subTest(collection_type=collection_type):
                data = {
                    **self.valid_data,
                    "input_name": "Huiles alimentaires usagées d'origine animale",
                    "collection_type": collection_type,
                }
                serializer = BiomethaneSupplyInputCreateSerializer(data=data)
                self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_other_input_clears_collection_type(self):
        """Test when input_name.name is not in waste list, collection_type is set to None."""
        data = {
            **self.valid_data,
            "input_name": "Maïs",
            "collection_type": BiomethaneSupplyInput.PRIVATE,
        }
        serializer = BiomethaneSupplyInputCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data["collection_type"])
