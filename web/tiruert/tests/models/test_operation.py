from unittest.mock import Mock, PropertyMock, patch

from django.test import TestCase

from core.models import Biocarburant, Entity
from tiruert.models import Operation


class OperationConstantsTest(TestCase):
    """Tests for Operation constants."""

    def test_api_creatable_types_contains_expected_values(self):
        """Should contain only TRANSFERT, EXPORTATION, EXPEDITION, TENEUR."""
        expected = [
            Operation.TRANSFERT,
            Operation.EXPORTATION,
            Operation.EXPEDITION,
            Operation.TENEUR,
        ]
        self.assertCountEqual(Operation.API_CREATABLE_TYPES, expected)

    def test_api_deletable_types_contains_expected_values(self):
        """Should contain only CESSION, TENEUR, TRANSFERT, EXPORTATION, EXPEDITION."""
        expected = [
            Operation.CESSION,
            Operation.TENEUR,
            Operation.TRANSFERT,
            Operation.EXPORTATION,
            Operation.EXPEDITION,
        ]
        self.assertCountEqual(Operation.API_DELETABLE_TYPES, expected)


class OperationVolumePropertyTest(TestCase):
    """Tests for Operation.volume_l property."""

    def test_volume_l_returns_annotated_volume_when_exists(self):
        """Should return _volume when it exists (from queryset annotation)."""
        operation = Operation()
        operation._volume = 1500.0

        result = operation.volume_l
        self.assertEqual(result, 1500.0)

    def test_volume_l_returns_base_volume_when_no_annotation(self):
        """Should return volume property when _volume doesn't exist."""
        operation = Operation()

        # Mock the volume property to return a value
        with patch.object(type(operation), "volume", new_callable=PropertyMock) as mock_volume:
            mock_volume.return_value = 1000.0

            result = operation.volume_l
            self.assertEqual(result, 1000.0)

    def test_volume_l_handles_none_annotation(self):
        """Should return base volume when _volume is None."""
        operation = Operation()
        operation._volume = None

        with patch.object(type(operation), "volume", new_callable=PropertyMock) as mock_volume:
            mock_volume.return_value = 2000.0

            result = operation.volume_l
            self.assertEqual(result, 2000.0)


class OperationQuantityMethodTest(TestCase):
    """Tests for Operation.quantity(unit) method."""

    def test_quantity_returns_annotated_quantity_when_exists(self):
        """Should return rounded _quantity when it exists (from queryset annotation)."""
        operation = Operation()
        operation._quantity = 1234.5678

        result = operation.quantity(unit="l")

        self.assertEqual(result, 1234.57)

    def test_quantity_calculates_from_volume_when_no_annotation(self):
        """Should calculate quantity from volume_l when _quantity doesn't exist."""
        operation = Operation()

        with patch.object(type(operation), "volume_l", new_callable=PropertyMock) as mock_volume_l:
            mock_volume_l.return_value = 1000.0
            with patch.object(operation, "volume_to_quantity", return_value=1000.0) as mock_convert:
                result = operation.quantity(unit="l")

                mock_convert.assert_called_once_with(1000.0, "l")
                self.assertEqual(result, 1000.0)

    def test_quantity_converts_to_mj(self):
        """Should convert volume to MJ using biofuel.pci_litre."""
        operation = Operation()

        with patch.object(type(operation), "volume_l", new_callable=PropertyMock) as mock_volume_l:
            mock_volume_l.return_value = 1000.0
            with patch.object(operation, "volume_to_quantity", return_value=36000.0) as mock_convert:
                result = operation.quantity(unit="mj")

                mock_convert.assert_called_once_with(1000.0, "mj")
                self.assertEqual(result, 36000.0)

    def test_quantity_converts_to_kg(self):
        """Should convert volume to KG using biofuel.masse_volumique."""
        operation = Operation()

        with patch.object(type(operation), "volume_l", new_callable=PropertyMock) as mock_volume_l:
            mock_volume_l.return_value = 1000.0
            with patch.object(operation, "volume_to_quantity", return_value=850.0) as mock_convert:
                result = operation.quantity(unit="kg")

                mock_convert.assert_called_once_with(1000.0, "kg")
                self.assertEqual(result, 850.0)

    def test_quantity_uses_liters_by_default(self):
        """Should use liters as default unit."""
        operation = Operation()

        with patch.object(type(operation), "volume_l", new_callable=PropertyMock) as mock_volume_l:
            mock_volume_l.return_value = 500.0
            with patch.object(operation, "volume_to_quantity", return_value=500.0):
                result = operation.quantity()

                self.assertEqual(result, 500.0)


class OperationAvoidedEmissionsPropertyTest(TestCase):
    """Tests for Operation.avoided_emissions property."""

    def test_avoided_emissions_sums_all_detail_emissions(self):
        """Should sum avoided_emissions from all details."""
        operation = Operation()

        detail1 = Mock()
        detail1.avoided_emissions = 100.5
        detail2 = Mock()
        detail2.avoided_emissions = 200.3
        detail3 = Mock()
        detail3.avoided_emissions = 150.7

        # Mock the details relationship
        details_mock = Mock()
        details_mock.all = Mock(return_value=[detail1, detail2, detail3])

        with patch.object(Operation, "details", PropertyMock(return_value=details_mock)):
            result = operation.avoided_emissions

        self.assertEqual(result, 451.50)

    def test_avoided_emissions_returns_zero_when_no_details(self):
        """Should return 0 when operation has no details."""
        operation = Operation()

        details_mock = Mock()
        details_mock.all = Mock(return_value=[])

        with patch.object(Operation, "details", PropertyMock(return_value=details_mock)):
            result = operation.avoided_emissions

        self.assertEqual(result, 0.0)

    def test_avoided_emissions_rounds_to_two_decimals(self):
        """Should round result to 2 decimal places."""
        operation = Operation()

        detail1 = Mock()
        detail1.avoided_emissions = 100.123456
        detail2 = Mock()
        detail2.avoided_emissions = 200.456789

        details_mock = Mock()
        details_mock.all = Mock(return_value=[detail1, detail2])

        with patch.object(Operation, "details", PropertyMock(return_value=details_mock)):
            result = operation.avoided_emissions

        # 100.123456 + 200.456789 = 300.580245, rounded to 300.58
        self.assertEqual(result, 300.58)


class OperationVolumeToQuantityMethodTest(TestCase):
    """Tests for Operation.volume_to_quantity(volume, unit) method."""

    def test_volume_to_quantity_mj(self):
        """Should convert volume to MJ using pci_litre."""
        biofuel = Biocarburant.objects.create(
            code="TEST_MJ",
            name="Test Biofuel MJ",
            pci_litre=36.0,
        )
        operation = Operation(biofuel=biofuel)

        result = operation.volume_to_quantity(1000.0, "mj")
        self.assertEqual(result, 36000.0)

    def test_volume_to_quantity_kg(self):
        """Should convert volume to KG using masse_volumique."""
        biofuel = Biocarburant.objects.create(
            code="TEST_KG",
            name="Test Biofuel KG",
            masse_volumique=0.85,
        )
        operation = Operation(biofuel=biofuel)

        result = operation.volume_to_quantity(1000.0, "kg")
        self.assertEqual(result, 850.0)

    def test_volume_to_quantity_liters(self):
        """Should return volume unchanged for liters."""
        operation = Operation()

        result = operation.volume_to_quantity(1500.0, "l")
        self.assertEqual(result, 1500.0)

    def test_volume_to_quantity_unknown_unit(self):
        """Should return volume unchanged for unknown units."""
        operation = Operation()

        result = operation.volume_to_quantity(2000.0, "unknown")
        self.assertEqual(result, 2000.0)


class OperationSectorPropertyTest(TestCase):
    """Tests for Operation.sector property."""

    def test_sector_returns_essence_when_compatible_essence(self):
        """Should return ESSENCE when biofuel is compatible with essence."""
        biofuel = Biocarburant.objects.create(
            code="ETH",
            name="Ethanol",
            compatible_essence=True,
            compatible_diesel=False,
        )
        operation = Operation(biofuel=biofuel)

        result = operation.sector
        self.assertEqual(result, Operation.ESSENCE)

    def test_sector_returns_gazole_when_compatible_diesel(self):
        """Should return GAZOLE when biofuel is compatible with diesel."""
        biofuel = Biocarburant.objects.create(
            code="EMHV",
            name="EMHV",
            compatible_essence=False,
            compatible_diesel=True,
        )
        operation = Operation(biofuel=biofuel)

        result = operation.sector
        self.assertEqual(result, Operation.GAZOLE)

    def test_sector_returns_carbureacteur_when_saf_biofuel(self):
        """Should return CARBUREACTEUR when biofuel code is in SAF_BIOFUEL_TYPES."""
        from saf.models.constants import SAF_BIOFUEL_TYPES

        # Use the first SAF biofuel type from constants
        saf_code = list(SAF_BIOFUEL_TYPES)[0]
        biofuel = Biocarburant.objects.create(
            code=saf_code,
            name=f"SAF {saf_code}",
            compatible_essence=False,
            compatible_diesel=False,
        )
        operation = Operation(biofuel=biofuel)

        result = operation.sector
        self.assertEqual(result, Operation.CARBUREACTEUR)

    def test_sector_returns_none_when_no_match(self):
        """Should return None when biofuel doesn't match any sector."""
        biofuel = Biocarburant.objects.create(
            code="UNKNOWN",
            name="Unknown Biofuel",
            compatible_essence=False,
            compatible_diesel=False,
        )
        operation = Operation(biofuel=biofuel)

        result = operation.sector
        self.assertIsNone(result)


class OperationIsCreditMethodTest(TestCase):
    """Tests for Operation.is_credit(entity) method."""

    fixtures = [
        "json/entities.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        self.other_entity = Entity.objects.filter(entity_type=Entity.OPERATOR).last()

    def test_is_credit_returns_true_when_credited_entity_matches(self):
        """Should return True when credited_entity.id matches the given entity."""
        operation = Operation(credited_entity=self.entity)
        result = operation.is_credit(self.entity.id)
        self.assertTrue(result)

    def test_is_credit_returns_false_when_credited_entity_does_not_match(self):
        """Should return False when credited_entity.id doesn't match."""
        operation = Operation(credited_entity=self.entity)
        result = operation.is_credit(self.other_entity.id)
        self.assertFalse(result)

    def test_is_credit_returns_false_when_credited_entity_is_none(self):
        """Should return False when credited_entity is None."""
        operation = Operation(credited_entity=None)
        result = operation.is_credit(self.entity.id)
        self.assertFalse(result)

    def test_is_credit_handles_string_entity_id(self):
        """Should handle entity parameter as string and convert to int."""
        operation = Operation(credited_entity=self.entity)
        result = operation.is_credit(str(self.entity.id))
        self.assertTrue(result)


class OperationIsAcquisitionMethodTest(TestCase):
    """Tests for Operation.is_acquisition(entity_id) method."""

    fixtures = [
        "json/entities.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        self.other_entity = Entity.objects.filter(entity_type=Entity.OPERATOR).last()

    def test_is_acquisition_returns_true_when_credited_entity_matches_and_type_is_cession(self):
        """Should return True when credited_entity matches and type is CESSION."""
        operation = Operation(
            credited_entity=self.entity,
            type=Operation.CESSION,
        )

        result = operation.is_acquisition(self.entity.id)
        self.assertTrue(result)

    def test_is_acquisition_returns_false_when_credited_entity_matches_but_type_is_not_cession(self):
        """Should return False when credited_entity matches but type is not CESSION."""
        operation = Operation(
            credited_entity=self.entity,
            type=Operation.TENEUR,
        )

        result = operation.is_acquisition(self.entity.id)
        self.assertFalse(result)

    def test_is_acquisition_returns_false_when_type_is_cession_but_entity_does_not_match(self):
        """Should return False when type is CESSION but credited_entity doesn't match."""
        operation = Operation(
            credited_entity=self.entity,
            type=Operation.CESSION,
        )

        result = operation.is_acquisition(self.other_entity.id)
        self.assertFalse(result)

    def test_is_acquisition_returns_false_when_credited_entity_is_none(self):
        """Should return False when credited_entity is None."""
        operation = Operation(
            credited_entity=None,
            type=Operation.CESSION,
        )

        result = operation.is_acquisition(self.entity.id)
        self.assertFalse(result)

    def test_is_acquisition_handles_string_entity_id(self):
        """Should handle entity_id parameter as string and convert to int."""
        operation = Operation(
            credited_entity=self.entity,
            type=Operation.CESSION,
        )

        result = operation.is_acquisition(str(self.entity.id))
        self.assertTrue(result)
