from django.test import TestCase

from core.models import Entity, MatierePremiere
from tiruert.models.operation import Operation
from tiruert.serializers.objective import (
    MainObjectiveSerializer,
    ObjectiveAdminInputSerializer,
    ObjectiveCategorySerializer,
    ObjectiveInputSerializer,
    ObjectiveOutputSerializer,
    ObjectiveSectorSerializer,
    ObjectiveSerializer,
)


class ObjectiveSerializerTest(TestCase):
    """Unit tests for ObjectiveSerializer."""

    def test_serializes_valid_objective_data(self):
        """Test ObjectiveSerializer correctly serializes valid data."""
        data = {
            "target_mj": 1000000.123,
            "target_type": "CAP",
            "penalty": 100,
            "target_percent": 0.1,
        }

        serializer = ObjectiveSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["target_type"], "CAP")
        self.assertEqual(serializer.validated_data["penalty"], 100)

    def test_serializes_instance_with_rounded_float(self):
        """Test ObjectiveSerializer rounds float values when serializing."""
        instance = {
            "target_mj": 1000000.12345,
            "target_type": "MIN",
            "penalty": 50,
            "target_percent": 0.15,
        }

        serializer = ObjectiveSerializer(instance)
        data = serializer.data

        self.assertIn("target_mj", data)
        self.assertEqual(data["target_type"], "MIN")

    def test_missing_required_fields_are_invalid(self):
        """Test ObjectiveSerializer requires all fields."""
        required_fields = ["target_mj", "target_type", "penalty", "target_percent"]

        for field_to_omit in required_fields:
            with self.subTest(field=field_to_omit):
                data = {
                    "target_mj": 1000000,
                    "target_type": "CAP",
                    "penalty": 100,
                    "target_percent": 0.1,
                }
                del data[field_to_omit]
                serializer = ObjectiveSerializer(data=data)

                self.assertFalse(serializer.is_valid())
                self.assertIn(field_to_omit, serializer.errors)


class ObjectiveSectorSerializerTest(TestCase):
    """Unit tests for ObjectiveSectorSerializer."""

    def test_serializes_valid_sector_data(self):
        """Test ObjectiveSectorSerializer correctly serializes valid sector data."""
        data = {
            "code": "ESSENCE",
            "pending_teneur": 5000.0,
            "declared_teneur": 3000.0,
            "available_balance": 10000.0,
            "unit": "mj",
            "objective": {
                "target_mj": 8000.0,
                "target_type": "MIN",
                "penalty": 50,
                "target_percent": 0.08,
            },
        }

        serializer = ObjectiveSectorSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["code"], "ESSENCE")

    def test_rejects_invalid_sector_code(self):
        """Test ObjectiveSectorSerializer rejects invalid sector codes."""
        data = {
            "code": "INVALID_SECTOR",
            "pending_teneur": 5000.0,
            "declared_teneur": 3000.0,
            "available_balance": 10000.0,
            "unit": "mj",
            "objective": {
                "target_mj": 8000.0,
                "target_type": "MIN",
                "penalty": 50,
                "target_percent": 0.08,
            },
        }

        serializer = ObjectiveSectorSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)

    def test_accepts_all_valid_sector_codes(self):
        """Test ObjectiveSectorSerializer accepts all valid sector codes."""
        valid_codes = [code for code, _ in Operation.SECTOR_CODE_CHOICES]
        base_data = {
            "pending_teneur": 5000.0,
            "declared_teneur": 3000.0,
            "available_balance": 10000.0,
            "unit": "mj",
            "objective": {
                "target_mj": 8000.0,
                "target_type": "MIN",
                "penalty": 50,
                "target_percent": 0.08,
            },
        }

        for code in valid_codes:
            with self.subTest(code=code):
                data = {**base_data, "code": code}
                serializer = ObjectiveSectorSerializer(data=data)

                self.assertTrue(serializer.is_valid(), f"Code {code} should be valid")

    def test_serializes_instance(self):
        """Test ObjectiveSectorSerializer correctly serializes instance."""
        instance = {
            "code": "GAZOLE",
            "pending_teneur": 5000.5,
            "declared_teneur": 3000.3,
            "available_balance": 10000.1,
            "unit": "mj",
            "objective": {
                "target_mj": 8000.0,
                "target_type": "MIN",
                "penalty": 50,
                "target_percent": 0.08,
            },
        }

        serializer = ObjectiveSectorSerializer(instance)
        data = serializer.data

        self.assertEqual(data["code"], "GAZOLE")
        self.assertIn("objective", data)


class ObjectiveCategorySerializerTest(TestCase):
    """Unit tests for ObjectiveCategorySerializer."""

    def test_serializes_valid_category_data(self):
        """Test ObjectiveCategorySerializer correctly serializes valid category data."""
        data = {
            "code": "CONV",
            "pending_teneur": 5000.0,
            "declared_teneur": 3000.0,
            "available_balance": 10000.0,
            "unit": "mj",
            "objective": {
                "target_mj": 8000.0,
                "target_type": "CAP",
                "penalty": 100,
                "target_percent": 0.07,
            },
        }

        serializer = ObjectiveCategorySerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["code"], "CONV")

    def test_rejects_invalid_category_code(self):
        """Test ObjectiveCategorySerializer rejects invalid category codes."""
        data = {
            "code": "INVALID_CATEGORY",
            "pending_teneur": 5000.0,
            "declared_teneur": 3000.0,
            "available_balance": 10000.0,
            "unit": "mj",
            "objective": {
                "target_mj": 8000.0,
                "target_type": "CAP",
                "penalty": 100,
                "target_percent": 0.07,
            },
        }

        serializer = ObjectiveCategorySerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)

    def test_accepts_all_valid_category_codes(self):
        """Test ObjectiveCategorySerializer accepts all valid category codes."""
        valid_codes = [code for code, _ in MatierePremiere.MP_CATEGORIES]
        base_data = {
            "pending_teneur": 5000.0,
            "declared_teneur": 3000.0,
            "available_balance": 10000.0,
            "unit": "mj",
            "objective": {
                "target_mj": 8000.0,
                "target_type": "CAP",
                "penalty": 100,
                "target_percent": 0.07,
            },
        }

        for code in valid_codes:
            with self.subTest(code=code):
                data = {**base_data, "code": code}
                serializer = ObjectiveCategorySerializer(data=data)

                self.assertTrue(serializer.is_valid(), f"Code {code} should be valid")


class MainObjectiveSerializerTest(TestCase):
    """Unit tests for MainObjectiveSerializer."""

    def test_serializes_valid_main_objective_data(self):
        """Test MainObjectiveSerializer correctly serializes valid data."""
        data = {
            "available_balance": 150000.0,
            "target": 200000.0,
            "pending_teneur": 50000.0,
            "declared_teneur": 30000.0,
            "unit": "tCO2",
            "penalty": 1000,
            "target_percent": 0.1,
            "energy_basis": 10000000.0,
        }

        serializer = MainObjectiveSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["unit"], "tCO2")

    def test_missing_required_fields_are_invalid(self):
        """Test MainObjectiveSerializer requires all fields."""
        complete_data = {
            "available_balance": 150000.0,
            "target": 200000.0,
            "pending_teneur": 50000.0,
            "declared_teneur": 30000.0,
            "unit": "tCO2",
            "penalty": 1000,
            "target_percent": 0.1,
            "energy_basis": 10000000.0,
        }

        for field_to_omit in complete_data.keys():
            with self.subTest(field=field_to_omit):
                data = {k: v for k, v in complete_data.items() if k != field_to_omit}
                serializer = MainObjectiveSerializer(data=data)

                self.assertFalse(serializer.is_valid())
                self.assertIn(field_to_omit, serializer.errors)

    def test_serializes_instance_with_rounded_floats(self):
        """Test MainObjectiveSerializer rounds float values when serializing."""
        instance = {
            "available_balance": 150000.12345,
            "target": 200000.6789,
            "pending_teneur": 50000.111,
            "declared_teneur": 30000.999,
            "unit": "tCO2",
            "penalty": 1000,
            "target_percent": 0.1,
            "energy_basis": 10000000.0,
        }

        serializer = MainObjectiveSerializer(instance)
        data = serializer.data

        self.assertIn("available_balance", data)
        self.assertIn("pending_teneur", data)


class ObjectiveOutputSerializerTest(TestCase):
    """Unit tests for ObjectiveOutputSerializer."""

    def test_serializes_complete_objective_output(self):
        """Test ObjectiveOutputSerializer correctly serializes complete output."""
        data = {
            "main": {
                "available_balance": 150000.0,
                "target": 200000.0,
                "pending_teneur": 50000.0,
                "declared_teneur": 30000.0,
                "unit": "tCO2",
                "penalty": 1000,
                "target_percent": 0.1,
                "energy_basis": 10000000.0,
            },
            "sectors": [
                {
                    "code": "ESSENCE",
                    "pending_teneur": 25000.0,
                    "declared_teneur": 15000.0,
                    "available_balance": 75000.0,
                    "unit": "mj",
                    "objective": {
                        "target_mj": 100000.0,
                        "target_type": "MIN",
                        "penalty": 50,
                        "target_percent": 0.1,
                    },
                },
            ],
            "categories": [
                {
                    "code": "CONV",
                    "pending_teneur": 30000.0,
                    "declared_teneur": 20000.0,
                    "available_balance": 90000.0,
                    "unit": "mj",
                    "objective": {
                        "target_mj": 120000.0,
                        "target_type": "CAP",
                        "penalty": 100,
                        "target_percent": 0.07,
                    },
                },
            ],
        }

        serializer = ObjectiveOutputSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertIn("main", serializer.validated_data)
        self.assertIn("sectors", serializer.validated_data)
        self.assertIn("categories", serializer.validated_data)

    def test_serializes_with_empty_sectors_and_categories(self):
        """Test ObjectiveOutputSerializer accepts empty sectors and categories lists."""
        data = {
            "main": {
                "available_balance": 150000.0,
                "target": 200000.0,
                "pending_teneur": 50000.0,
                "declared_teneur": 30000.0,
                "unit": "tCO2",
                "penalty": 1000,
                "target_percent": 0.1,
                "energy_basis": 10000000.0,
            },
            "sectors": [],
            "categories": [],
        }

        serializer = ObjectiveOutputSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data["sectors"]), 0)
        self.assertEqual(len(serializer.validated_data["categories"]), 0)

    def test_serializes_with_multiple_sectors_and_categories(self):
        """Test ObjectiveOutputSerializer handles multiple sectors and categories."""
        data = {
            "main": {
                "available_balance": 150000.0,
                "target": 200000.0,
                "pending_teneur": 50000.0,
                "declared_teneur": 30000.0,
                "unit": "tCO2",
                "penalty": 1000,
                "target_percent": 0.1,
                "energy_basis": 10000000.0,
            },
            "sectors": [
                {
                    "code": "ESSENCE",
                    "pending_teneur": 25000.0,
                    "declared_teneur": 15000.0,
                    "available_balance": 75000.0,
                    "unit": "mj",
                    "objective": {
                        "target_mj": 100000.0,
                        "target_type": "MIN",
                        "penalty": 50,
                        "target_percent": 0.1,
                    },
                },
                {
                    "code": "GAZOLE",
                    "pending_teneur": 20000.0,
                    "declared_teneur": 10000.0,
                    "available_balance": 60000.0,
                    "unit": "mj",
                    "objective": {
                        "target_mj": 80000.0,
                        "target_type": "MIN",
                        "penalty": 50,
                        "target_percent": 0.08,
                    },
                },
            ],
            "categories": [
                {
                    "code": "CONV",
                    "pending_teneur": 30000.0,
                    "declared_teneur": 20000.0,
                    "available_balance": 90000.0,
                    "unit": "mj",
                    "objective": {
                        "target_mj": 120000.0,
                        "target_type": "CAP",
                        "penalty": 100,
                        "target_percent": 0.07,
                    },
                },
                {
                    "code": MatierePremiere.IXB,  # "ANN-IX-B"
                    "pending_teneur": 15000.0,
                    "declared_teneur": 10000.0,
                    "available_balance": 45000.0,
                    "unit": "mj",
                    "objective": {
                        "target_mj": 60000.0,
                        "target_type": "MIN",
                        "penalty": 75,
                        "target_percent": 0.035,
                    },
                },
            ],
        }

        serializer = ObjectiveOutputSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(len(serializer.validated_data["sectors"]), 2)
        self.assertEqual(len(serializer.validated_data["categories"]), 2)

    def test_missing_main_is_invalid(self):
        """Test ObjectiveOutputSerializer requires main field."""
        data = {
            "sectors": [],
            "categories": [],
        }

        serializer = ObjectiveOutputSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("main", serializer.errors)


class ObjectiveInputSerializerTest(TestCase):
    """Unit tests for ObjectiveInputSerializer."""

    def test_serializes_valid_input_data(self):
        """Test ObjectiveInputSerializer correctly validates valid input data."""
        data = {
            "entity_id": 1,
            "year": 2024,
            "date_from": "2024-01-01",
        }

        serializer = ObjectiveInputSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["entity_id"], 1)
        self.assertEqual(serializer.validated_data["year"], 2024)

    def test_serializes_with_optional_date_to(self):
        """Test ObjectiveInputSerializer accepts optional date_to field."""
        data = {
            "entity_id": 1,
            "year": 2024,
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
        }

        serializer = ObjectiveInputSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertIn("date_to", serializer.validated_data)

    def test_missing_required_fields_are_invalid(self):
        """Test ObjectiveInputSerializer requires entity_id, year, and date_from."""
        required_fields = ["entity_id", "year", "date_from"]
        complete_data = {
            "entity_id": 1,
            "year": 2024,
            "date_from": "2024-01-01",
        }

        for field_to_omit in required_fields:
            with self.subTest(field=field_to_omit):
                data = {k: v for k, v in complete_data.items() if k != field_to_omit}
                serializer = ObjectiveInputSerializer(data=data)

                self.assertFalse(serializer.is_valid())
                self.assertIn(field_to_omit, serializer.errors)

    def test_rejects_invalid_date_format(self):
        """Test ObjectiveInputSerializer rejects invalid date format."""
        data = {
            "entity_id": 1,
            "year": 2024,
            "date_from": "invalid-date",
        }

        serializer = ObjectiveInputSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("date_from", serializer.errors)

    def test_rejects_non_integer_entity_id(self):
        """Test ObjectiveInputSerializer rejects non-integer entity_id."""
        data = {
            "entity_id": "not-an-integer",
            "year": 2024,
            "date_from": "2024-01-01",
        }

        serializer = ObjectiveInputSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("entity_id", serializer.errors)

    def test_rejects_non_integer_year(self):
        """Test ObjectiveInputSerializer rejects non-integer year."""
        data = {
            "entity_id": 1,
            "year": "twenty-twenty-four",
            "date_from": "2024-01-01",
        }

        serializer = ObjectiveInputSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("year", serializer.errors)


class ObjectiveAdminInputSerializerTest(TestCase):
    """Unit tests for ObjectiveAdminInputSerializer."""

    fixtures = [
        "json/countries.json",
        "json/entities.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for all tests."""
        # Get or create a tiruert-liable entity
        cls.liable_entity = Entity.objects.filter(is_tiruert_liable=True).first()
        if not cls.liable_entity:
            cls.liable_entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
            if cls.liable_entity:
                cls.liable_entity.is_tiruert_liable = True
                cls.liable_entity.save()

        cls.non_liable_entity = Entity.objects.filter(is_tiruert_liable=False).first()

    def test_serializes_valid_admin_input_data(self):
        """Test ObjectiveAdminInputSerializer validates valid admin input."""
        if not self.liable_entity:
            self.skipTest("No tiruert-liable entity available")

        data = {
            "entity_id": 1,
            "year": 2024,
            "date_from": "2024-01-01",
            "selected_entity_id": self.liable_entity.id,
        }

        serializer = ObjectiveAdminInputSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["selected_entity_id"], self.liable_entity)

    def test_inherits_from_objective_input_serializer(self):
        """Test ObjectiveAdminInputSerializer inherits ObjectiveInputSerializer fields."""
        if not self.liable_entity:
            self.skipTest("No tiruert-liable entity available")

        # Missing inherited required fields should fail
        data = {
            "selected_entity_id": self.liable_entity.id,
        }

        serializer = ObjectiveAdminInputSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("entity_id", serializer.errors)
        self.assertIn("year", serializer.errors)
        self.assertIn("date_from", serializer.errors)

    def test_requires_selected_entity_id(self):
        """Test ObjectiveAdminInputSerializer requires selected_entity_id."""
        data = {
            "entity_id": 1,
            "year": 2024,
            "date_from": "2024-01-01",
        }

        serializer = ObjectiveAdminInputSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("selected_entity_id", serializer.errors)

    def test_rejects_non_liable_entity(self):
        """Test ObjectiveAdminInputSerializer rejects entities that are not tiruert-liable."""
        if not self.non_liable_entity:
            self.skipTest("No non-tiruert-liable entity available")

        data = {
            "entity_id": 1,
            "year": 2024,
            "date_from": "2024-01-01",
            "selected_entity_id": self.non_liable_entity.id,
        }

        serializer = ObjectiveAdminInputSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("selected_entity_id", serializer.errors)

    def test_rejects_non_existent_entity(self):
        """Test ObjectiveAdminInputSerializer rejects non-existent entity IDs."""
        data = {
            "entity_id": 1,
            "year": 2024,
            "date_from": "2024-01-01",
            "selected_entity_id": 99999,  # Non-existent ID
        }

        serializer = ObjectiveAdminInputSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("selected_entity_id", serializer.errors)
