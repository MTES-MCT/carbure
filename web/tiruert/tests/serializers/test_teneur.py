from django.test import TestCase

from core.models import Biocarburant, Entity, MatierePremiere
from tiruert.serializers.teneur import (
    SimulationInputSerializer,
    SimulationLotOutputSerializer,
    SimulationMinMaxInputSerializer,
    SimulationMinMaxOutputSerializer,
    SimulationOutputSerializer,
)
from transactions.models import Depot


class SimulationInputSerializerTest(TestCase):
    """Test SimulationInputSerializer validation and serialization."""

    fixtures = [
        "json/biofuels.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Create test data once for all tests."""
        cls.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        cls.biofuel = Biocarburant.objects.first()
        cls.depot = Depot.objects.first()

    def test_all_required_fields_present_is_valid(self):
        """Test that serializer is valid when all required fields are present."""
        data = {
            "biofuel": self.biofuel.id,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity.id,
            "target_volume": 1000.0,
            "target_emission": 1.5,
        }

        serializer = SimulationInputSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_all_fields_with_optional_is_valid(self):
        """Test serializer is valid with all fields including optional ones."""
        data = {
            "biofuel": self.biofuel.id,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity.id,
            "target_volume": 1000.0,
            "target_emission": 1.5,
            "max_n_batches": 5,
            "enforced_volumes": [100, 200],
            "unit": "l",
            "from_depot": self.depot.id,
            "ges_bound_min": 0.5,
            "ges_bound_max": 2.0,
        }

        serializer = SimulationInputSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_missing_required_fields_are_invalid(self):
        """Test that missing required fields raise validation errors."""
        required_fields = {
            "biofuel": self.biofuel.id,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity.id,
            "target_volume": 1000.0,
            "target_emission": 1.5,
        }

        for field_to_omit in required_fields.keys():
            with self.subTest(field=field_to_omit):
                data = {k: v for k, v in required_fields.items() if k != field_to_omit}
                serializer = SimulationInputSerializer(data=data)

                self.assertFalse(serializer.is_valid())
                self.assertIn(field_to_omit, serializer.errors)


class SimulationOutputSerializerTest(TestCase):
    """Test SimulationOutputSerializer serialization."""

    def test_serializes_empty_selected_lots(self):
        """Test serialization with empty selected_lots list."""
        data = {"selected_lots": [], "fun": 0.5}

        serializer = SimulationOutputSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data["selected_lots"]), 0)

    def test_serializes_multiple_selected_lots(self):
        """Test serialization with multiple selected lots."""
        data = {
            "selected_lots": [
                {"lot_id": 1, "volume": 100.0, "emission_rate_per_mj": 50.0},
                {"lot_id": 2, "volume": 200.0, "emission_rate_per_mj": 60.0},
            ],
            "fun": 1.2,
        }

        serializer = SimulationOutputSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data["selected_lots"]), 2)

    def test_fun_is_float(self):
        """Test that fun field is a float."""
        data = {"selected_lots": [], "fun": 3.14}

        serializer = SimulationOutputSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertIsInstance(serializer.validated_data["fun"], float)


class SimulationLotOutputSerializerTest(TestCase):
    """Test SimulationLotOutputSerializer serialization."""

    def test_field_types_and_precision(self):
        """Test field types and decimal precision."""
        test_cases = [
            # (data, field_checks)
            (
                {"lot_id": 42, "volume": 123.45, "emission_rate_per_mj": 55.5},
                [
                    ("lot_id", 42, int),
                    ("volume", 123.45, None),  # Check float conversion
                    ("emission_rate_per_mj", 55.5, float),
                ],
            ),
            (
                {"lot_id": 99, "volume": 100.0, "emission_rate_per_mj": 50.0},
                [("lot_id", 99, int)],
            ),
            (
                {"lot_id": 1, "volume": 123.456789, "emission_rate_per_mj": 50.0},
                [("volume", 123.456789, None)],  # High precision
            ),
            (
                {"lot_id": 1, "volume": 100.0, "emission_rate_per_mj": 62.5},
                [("emission_rate_per_mj", 62.5, float)],
            ),
        ]

        for data, checks in test_cases:
            with self.subTest(data=data):
                serializer = SimulationLotOutputSerializer(data=data)
                self.assertTrue(serializer.is_valid())

                for field, expected_value, expected_type in checks:
                    actual_value = serializer.validated_data[field]
                    if field == "volume":
                        actual_value = float(actual_value)
                    self.assertEqual(actual_value, expected_value)
                    if expected_type:
                        self.assertIsInstance(serializer.validated_data[field], expected_type)


class SimulationMinMaxInputSerializerTest(TestCase):
    """Test SimulationMinMaxInputSerializer validation."""

    fixtures = [
        "json/biofuels.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Create test data once for all tests."""
        cls.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        cls.biofuel = Biocarburant.objects.first()
        cls.depot = Depot.objects.first()

    def test_required_fields_present_is_valid(self):
        """Test that serializer is valid with only required fields."""
        data = {
            "biofuel": self.biofuel.id,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity.id,
            "target_volume": 1000.0,
        }

        serializer = SimulationMinMaxInputSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_target_emission_not_required(self):
        """Test that target_emission is not required (difference with SimulationInputSerializer)."""
        data = {
            "biofuel": self.biofuel.id,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity.id,
            "target_volume": 1000.0,
            # target_emission omitted - should still be valid
        }

        serializer = SimulationMinMaxInputSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertNotIn("target_emission", serializer.validated_data)

    def test_all_fields_with_optional_is_valid(self):
        """Test serializer is valid with all fields including optional ones."""
        data = {
            "biofuel": self.biofuel.id,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity.id,
            "target_volume": 1000.0,
            "unit": "mj",
            "from_depot": self.depot.id,
            "ges_bound_min": 0.5,
            "ges_bound_max": 2.0,
        }

        serializer = SimulationMinMaxInputSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_missing_required_fields_are_invalid(self):
        """Test that missing required fields raise validation errors."""
        required_fields = {
            "biofuel": self.biofuel.id,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity.id,
            "target_volume": 1000.0,
        }

        for field_to_omit in required_fields.keys():
            with self.subTest(field=field_to_omit):
                data = {k: v for k, v in required_fields.items() if k != field_to_omit}
                serializer = SimulationMinMaxInputSerializer(data=data)

                self.assertFalse(serializer.is_valid())
                self.assertIn(field_to_omit, serializer.errors)


class SimulationMinMaxOutputSerializerTest(TestCase):
    """Test SimulationMinMaxOutputSerializer serialization."""

    def test_field_types_and_negative_values(self):
        """Test that fields are floats and negative values are accepted."""
        test_cases = [
            ({"min_avoided_emissions": 1.5, "max_avoided_emissions": 3.2}, False),
            ({"min_avoided_emissions": -0.5, "max_avoided_emissions": 1.0}, True),
            ({"min_avoided_emissions": -2.0, "max_avoided_emissions": -0.5}, True),
        ]

        for data, has_negative in test_cases:
            with self.subTest(data=data):
                serializer = SimulationMinMaxOutputSerializer(data=data)

                self.assertTrue(serializer.is_valid())
                self.assertIsInstance(serializer.validated_data["min_avoided_emissions"], float)
                self.assertIsInstance(serializer.validated_data["max_avoided_emissions"], float)
                self.assertEqual(serializer.validated_data["min_avoided_emissions"], data["min_avoided_emissions"])
                self.assertEqual(serializer.validated_data["max_avoided_emissions"], data["max_avoided_emissions"])

                if has_negative:
                    self.assertLess(serializer.validated_data["min_avoided_emissions"], 0)
