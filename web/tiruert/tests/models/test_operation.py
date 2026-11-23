from unittest.mock import Mock, PropertyMock, patch

from django.test import TestCase

from core.models import Biocarburant, Entity
from tiruert.models import Operation


class OperationConstantsTest(TestCase):
    """Tests for Operation constants."""

    def test_api_creatable_types_contains_expected_values(self):
        """Should contain only TRANSFERT, EXPORTATION, EXPEDITION, TENEUR, DEVALUATION."""
        expected = [
            Operation.TRANSFERT,
            Operation.EXPORTATION,
            Operation.EXPEDITION,
            Operation.TENEUR,
            Operation.DEVALUATION,
        ]
        self.assertCountEqual(Operation.API_CREATABLE_TYPES, expected)

    def test_api_deletable_types_contains_expected_values(self):
        """Should contain only CESSION, TENEUR, TRANSFERT, EXPORTATION, EXPEDITION, DEVALUATION."""
        expected = [
            Operation.CESSION,
            Operation.TENEUR,
            Operation.TRANSFERT,
            Operation.EXPORTATION,
            Operation.EXPEDITION,
            Operation.DEVALUATION,
        ]
        self.assertCountEqual(Operation.API_DELETABLE_TYPES, expected)


class OperationVolumePropertyTest(TestCase):
    """Tests for Operation volume properties."""

    def test_volume_unsigned_sums_detail_volumes(self):
        """Should sum raw detail volumes."""
        operation = Operation()
        detail1 = Mock()
        detail1.volume = 100.2
        detail2 = Mock()
        detail2.volume = 50.3

        details_mock = Mock()
        details_mock.all = Mock(return_value=[detail1, detail2])

        with patch.object(Operation, "details", PropertyMock(return_value=details_mock)):
            self.assertEqual(operation.volume_unsigned, 150.5)

    def test_volume_returns_truncated_annotated_volume_when_exists(self):
        """Should return truncated _volume when it exists (from queryset annotation)."""
        operation = Operation()
        operation._volume = 1500.789

        result = operation.volume
        self.assertEqual(result, 1500.78)

    def test_volume_returns_unsigned_when_no_annotation(self):
        """Should return truncated unsigned volume when annotation is missing."""
        operation = Operation()

        with patch.object(type(operation), "volume_unsigned", new_callable=PropertyMock) as mock_volume_unsigned:
            mock_volume_unsigned.return_value = 321.987

            result = operation.volume
            self.assertEqual(result, 321.98)


class OperationEnergyPropertyTest(TestCase):
    """Tests for Operation.energy property."""

    def test_energy_returns_truncated_annotated_energy_when_exists(self):
        """Should return truncated _energy when it exists (from queryset annotation)."""
        operation = Operation()
        operation._energy = 4567.891

        result = operation.energy
        self.assertEqual(result, 4567)

    def test_energy_returns_unsigned_when_no_annotation(self):
        """Should compute unsigned energy when annotation is missing."""
        biofuel = Biocarburant.objects.create(
            code="TSTEU",
            name="Test Energy Unsigned",
            pci_litre=10.0,
        )
        operation = Operation(biofuel=biofuel)
        operation.renewable_energy_share = 0.5

        with patch.object(type(operation), "volume_unsigned", new_callable=PropertyMock) as mock_volume_unsigned:
            mock_volume_unsigned.return_value = 100.0

            result = operation.energy
            self.assertEqual(result, 500)


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

    def test_sector_returns_gpl_when_compatible_gpl(self):
        """Should return GPL when biofuel is compatible with GPL."""
        biofuel = Biocarburant.objects.create(
            code="HCGPL",
            name="HCGPL",
            compatible_essence=False,
            compatible_diesel=False,
            compatible_gpl=True,
        )
        operation = Operation(biofuel=biofuel)

        result = operation.sector
        self.assertEqual(result, Operation.GPL)

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
        "json/countries.json",
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
        "json/countries.json",
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
