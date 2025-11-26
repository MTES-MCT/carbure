from unittest import TestCase
from unittest.mock import Mock

from core.models import Biocarburant
from tiruert.serializers.balance import (
    BalanceBiofuelSerializer,
    BalanceByDepotSerializer,
    BalanceByLotSerializer,
    BalanceBySectorSerializer,
    BalanceDepotSerializer,
    BalanceLotSerializer,
    BalanceQuantitySerializer,
    BalanceSerializer,
    BaseBalanceSerializer,
)


class BalanceSerializersTest(TestCase):
    """Test basic serializers validation"""

    def test_balance_biofuel_serializer(self):
        """Test that BalanceBiofuelSerializer correctly serializes a biofuel object"""
        data = {"id": 1, "code": "ETH", "renewable_energy_share": 0.8}
        serializer = BalanceBiofuelSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["code"], "ETH")

    def test_balance_quantity_serializer(self):
        """Test that BalanceQuantitySerializer correctly serializes credit and debit values"""
        quantity = {"credit": 100.0, "debit": 50.0}
        serializer = BalanceQuantitySerializer(data=quantity)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["credit"], 100.0)
        self.assertEqual(serializer.validated_data["debit"], 50.0)

    def test_base_balance_serializer_get_initial_balance(self):
        """Test that BaseBalanceSerializer.get_initial_balance computes the initial balance correctly"""
        instance = {"available_balance": 150.0, "quantity": {"credit": 100.0, "debit": 50.0}}
        serializer = BaseBalanceSerializer()
        result = serializer.get_initial_balance(instance)
        self.assertEqual(result, 100.0)  # 150 - 100 + 50 = 100

    def test_balance_serializer_full(self):
        """Test that BalanceSerializer serializes all fields including nested biofuel and quantity"""
        data = {
            "sector": "ESSENCE",
            "customs_category": "CONV",
            "biofuel": {"id": 1, "code": "ETH", "renewable_energy_share": 0.8},
            "available_balance": 150.0,
            "quantity": {"credit": 100.0, "debit": 50.0},
            "pending_teneur": 0.0,
            "declared_teneur": 0.0,
            "pending_operations": 0,
            "unit": "liters",
            "ghg_reduction_min": 60.0,
            "ghg_reduction_max": 80.0,
            "saved_emissions": 42.0,
        }
        serializer = BalanceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["sector"], "ESSENCE")
        self.assertEqual(serializer.validated_data["biofuel"]["code"], "ETH")

    def test_balance_lot_serializer(self):
        """Test that BalanceLotSerializer serializes lot data including volume and emission rate"""
        data = {
            "lot": 42,
            "available_balance": 150.0,
            "volume": {"credit": 100.0, "debit": 50.0},
            "emission_rate_per_mj": 25.0,
        }
        serializer = BalanceLotSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["lot"], 42)

    def test_balance_depot_serializer(self):
        """Test that BalanceDepotSerializer serializes depot data including quantity and unit"""
        data = {
            "id": 7,
            "name": "Depot A",
            "quantity": {"credit": 100.0, "debit": 50.0},
            "unit": "l",
        }
        serializer = BalanceDepotSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "Depot A")


class BalanceBySectorSerializerTest(TestCase):
    """Test BalanceBySectorSerializer"""

    def test_balance_by_sector_serializer(self):
        """Test that BalanceBySectorSerializer inherits from BaseBalanceSerializer correctly"""
        data = {
            "sector": "ESSENCE",
            "available_balance": 150.0,
            "quantity": {"credit": 100.0, "debit": 50.0},
            "pending_teneur": 10.0,
            "declared_teneur": 5.0,
            "pending_operations": 3,
            "unit": "l",
        }
        serializer = BalanceBySectorSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["sector"], "ESSENCE")


class BalanceSerializerValidationTest(TestCase):
    """Test validation and edge cases for balance serializers"""

    def test_balance_quantity_serializer_with_defaults(self):
        """Test that BalanceQuantitySerializer applies default values for missing fields"""
        serializer = BalanceQuantitySerializer(data={})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["credit"], 0.0)
        self.assertEqual(serializer.validated_data["debit"], 0.0)

    def test_balance_serializer_with_invalid_sector(self):
        """Test that BalanceSerializer rejects invalid sector choices"""
        data = {
            "sector": "INVALID_SECTOR",
            "customs_category": "CONV",
            "biofuel": {"id": 1, "code": "ETH", "renewable_energy_share": 0.8},
            "available_balance": 150.0,
            "quantity": {"credit": 100.0, "debit": 50.0},
            "pending_teneur": 0.0,
            "declared_teneur": 0.0,
            "pending_operations": 0,
            "unit": "l",
            "ghg_reduction_min": 60.0,
            "ghg_reduction_max": 80.0,
            "saved_emissions": 42.0,
        }
        serializer = BalanceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("sector", serializer.errors)

    def test_balance_serializer_with_invalid_customs_category(self):
        """Test that BalanceSerializer rejects invalid customs_category choices"""
        data = {
            "sector": "ESSENCE",
            "customs_category": "INVALID_CATEGORY",
            "biofuel": {"id": 1, "code": "ETH", "renewable_energy_share": 0.8},
            "available_balance": 150.0,
            "quantity": {"credit": 100.0, "debit": 50.0},
            "pending_teneur": 0.0,
            "declared_teneur": 0.0,
            "pending_operations": 0,
            "unit": "l",
            "ghg_reduction_min": 60.0,
            "ghg_reduction_max": 80.0,
            "saved_emissions": 42.0,
        }
        serializer = BalanceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("customs_category", serializer.errors)

    def test_balance_by_lot_serializer_with_null_values(self):
        """Test that BalanceByLotSerializer accepts null values for optional fields"""
        data = {
            "customs_category": None,
            "biofuel": None,
            "lots": [],
        }
        serializer = BalanceByLotSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data["customs_category"])
        self.assertIsNone(serializer.validated_data["biofuel"])

    def test_get_initial_balance_with_negative_values(self):
        """Test that BaseBalanceSerializer.get_initial_balance works with negative values"""
        instance = {"available_balance": -50.0, "quantity": {"credit": 100.0, "debit": 30.0}}
        serializer = BaseBalanceSerializer()
        result = serializer.get_initial_balance(instance)
        self.assertEqual(result, -120.0)  # -50 - 100 + 30 = -120

    def test_balance_by_lot_prepare_data_with_empty_dict(self):
        """Test that BalanceByLotSerializer.prepare_data handles empty dictionary"""
        result = BalanceByLotSerializer.prepare_data({})
        self.assertEqual(result, [])

    def test_balance_by_depot_prepare_data_with_empty_dict(self):
        """Test that BalanceByDepotSerializer.prepare_data handles empty dictionary"""
        result = BalanceByDepotSerializer.prepare_data({})
        self.assertEqual(result, [])


class BalancePrepareDataAggregationTest(TestCase):
    """Test aggregation logic in prepare_data methods"""

    def test_balance_by_lot_prepare_data_aggregates_multiple_lots(self):
        """Test that BalanceByLotSerializer.prepare_data correctly groups and sums multiple lots"""
        balance_dict = {
            ("ESSENCE", "CONV", "ETH", 42): {
                "available_balance": 100.0,
                "quantity": {"credit": 50.0, "debit": 25.0},
                "emission_rate_per_mj": 25.0,
            },
            ("ESSENCE", "CONV", "ETH", 43): {
                "available_balance": 50.0,
                "quantity": {"credit": 30.0, "debit": 15.0},
                "emission_rate_per_mj": 26.0,
            },
            ("GAZOLE", "CONV", "EMHV", 44): {
                "available_balance": 200.0,
                "quantity": {"credit": 100.0, "debit": 50.0},
                "emission_rate_per_mj": 30.0,
            },
        }
        result = BalanceByLotSerializer.prepare_data(balance_dict)

        # Should have 2 groups: (CONV, ETH) and (CONV, EMHV)
        self.assertEqual(len(result), 2)

        # Find the ETH group
        eth_group = next((g for g in result if g["biofuel"] == "ETH"), None)
        self.assertIsNotNone(eth_group)
        self.assertEqual(len(eth_group["lots"]), 2)
        self.assertEqual(eth_group["available_balance"], 150.0)  # 100 + 50

        # Find the EMHV group
        emhv_group = next((g for g in result if g["biofuel"] == "EMHV"), None)
        self.assertIsNotNone(emhv_group)
        self.assertEqual(len(emhv_group["lots"]), 1)
        self.assertEqual(emhv_group["available_balance"], 200.0)

    def test_balance_by_depot_prepare_data_aggregates_multiple_depots(self):
        """Test that BalanceByDepotSerializer.prepare_data correctly groups and sums multiple depots"""
        depot_mock_1 = Mock()
        depot_mock_1.id = 7
        depot_mock_1.name = "Depot A"

        depot_mock_2 = Mock()
        depot_mock_2.id = 8
        depot_mock_2.name = "Depot B"

        biofuel = Biocarburant(id=1, code="ETH", renewable_energy_share=0.8)

        balance_dict = {
            ("ESSENCE", "CONV", "ETH", depot_mock_1): {
                "available_balance": 100.0,
                "quantity": {"credit": 50.0, "debit": 25.0},
                "unit": "l",
                "biofuel": biofuel,
            },
            ("ESSENCE", "CONV", "ETH", depot_mock_2): {
                "available_balance": 75.0,
                "quantity": {"credit": 40.0, "debit": 20.0},
                "unit": "l",
                "biofuel": biofuel,
            },
        }
        result = BalanceByDepotSerializer.prepare_data(balance_dict)

        # Should have 1 group: (CONV, ETH)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["customs_category"], "CONV")
        self.assertEqual(len(result[0]["depots"]), 2)
        self.assertEqual(result[0]["available_balance"], 175.0)  # 100 + 75

        # Verify both depots are present
        depot_names = [d["name"] for d in result[0]["depots"]]
        self.assertIn("Depot A", depot_names)
        self.assertIn("Depot B", depot_names)


class BalanceSerializationTest(TestCase):
    """Test serialization of Python objects to JSON"""

    def test_balance_serializer_serializes_instance(self):
        """Test that BalanceSerializer correctly serializes a Python dict instance to JSON"""
        biofuel_instance = {"id": 1, "code": "ETH", "renewable_energy_share": 0.8}
        instance = {
            "sector": "ESSENCE",
            "customs_category": "CONV",
            "biofuel": biofuel_instance,
            "available_balance": 150.0,
            "quantity": {"credit": 100.0, "debit": 50.0},
            "pending_teneur": 10.0,
            "declared_teneur": 5.0,
            "pending_operations": 3,
            "unit": "l",
            "ghg_reduction_min": 60.0,
            "ghg_reduction_max": 80.0,
            "saved_emissions": 42.0,
        }
        serializer = BalanceSerializer(instance)
        data = serializer.data

        # Verify all fields are present
        self.assertEqual(data["sector"], "ESSENCE")
        self.assertEqual(data["customs_category"], "CONV")
        self.assertEqual(data["biofuel"]["code"], "ETH")
        self.assertEqual(data["available_balance"], 150.0)
        self.assertEqual(data["quantity"]["credit"], 100.0)
        self.assertEqual(data["quantity"]["debit"], 50.0)
        # Verify initial_balance is calculated and present
        self.assertIn("initial_balance", data)
        self.assertEqual(data["initial_balance"], 100.0)  # 150 - 100 + 50

    def test_balance_by_sector_serializer_includes_initial_balance(self):
        """Test that BalanceBySectorSerializer includes calculated initial_balance in serialized data"""
        instance = {
            "sector": "ESSENCE",
            "available_balance": 200.0,
            "quantity": {"credit": 150.0, "debit": 100.0},
            "pending_teneur": 10.0,
            "declared_teneur": 5.0,
            "pending_operations": 5,
            "unit": "l",
        }
        serializer = BalanceBySectorSerializer(instance)
        data = serializer.data

        self.assertIn("initial_balance", data)
        self.assertEqual(data["initial_balance"], 150.0)  # 200 - 150 + 100
