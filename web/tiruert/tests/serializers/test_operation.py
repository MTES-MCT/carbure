from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework import serializers

from core.models import Biocarburant, MatierePremiere
from tiruert.models import Operation
from tiruert.serializers import OperationListSerializer, OperationSerializer
from tiruert.serializers.operation import (
    BaseOperationSerializer,
    OperationExcelRowSerializer,
    OperationInputSerializer,
    OperationUpdateSerializer,
)
from transactions.factories import CarbureLotFactory
from transactions.factories.production_site import ProductionSiteFactory
from transactions.models import Depot


class BaseOperationSerializerTest(TestCase):
    """Tests for BaseOperationSerializer delegation to model methods."""

    def _create_serializer(self, context=None):
        """Helper to create serializer with context."""
        if context is None:
            context = {}
        return BaseOperationSerializer(context=context)

    def test_get_volume_delegates_to_model(self):
        """Should delegate to instance.volume with default serializer behavior."""
        serializer = self._create_serializer()
        instance = Mock(spec=Operation)
        instance.volume = 1500.0

        result = serializer.get_volume(instance)

        self.assertEqual(result, 1500.0)

    def test_get_energy_delegates_to_model(self):
        """Should delegate to instance.energy with default serializer behavior."""
        serializer = self._create_serializer()
        instance = Mock(spec=Operation)
        instance.energy = 72000.0

        result = serializer.get_energy(instance)

        self.assertEqual(result, 72000.0)

    def test_get_fields_removes_details_when_not_requested(self):
        """Should not build the nested details field on list responses by default."""
        serializer = OperationListSerializer(context={"details": False})

        self.assertNotIn("details", serializer.fields)

    def test_get_fields_keeps_details_when_requested(self):
        """Should keep nested details field when explicit details mode is enabled."""
        serializer = OperationListSerializer(context={"details": True})

        self.assertIn("details", serializer.fields)

    def test_operation_list_serializer_uses_annotated_volume_energy_and_avoided_emissions(self):
        """List serializer should read pre-annotated numeric fields directly."""
        operation = Mock(spec=Operation)
        operation.id = 1
        operation._type = Operation.CESSION
        operation.status = Operation.PENDING
        operation._sector = Operation.ESSENCE
        operation.objective_sector = None
        operation.customs_category = MatierePremiere.CONV
        operation.biofuel = Biocarburant(
            id=1,
            code="ETH",
            renewable_energy_share=1.0,
            pci_litre=21.1,
            masse_volumique=0.79,
        )
        operation.renewable_energy_share = 1.0
        operation.credited_entity = Mock(id=1, name="Credited")
        operation.debited_entity = Mock(id=2, name="Debited")
        operation._entity = "Credited"
        operation.from_depot = Mock(id=10, name="From")
        operation.to_depot = Mock(id=11, name="To")
        operation._depot = "To"
        operation.export_country = None
        operation.created_at = None
        operation._volume = 123.456
        operation._energy = 4567.891
        operation._avoided_emissions = 78.901
        operation.declaration_year = 2024

        serializer = OperationListSerializer(operation, context={"details": False})

        self.assertEqual(serializer.data["volume"], 123.45)
        self.assertEqual(serializer.data["energy"], 4567)
        self.assertEqual(serializer.data["avoided_emissions"], 78.9)


class OperationSerializerTest(TestCase):
    """Tests for OperationSerializer delegation to model methods."""

    def _create_serializer(self, context=None):
        """Helper to create serializer with context."""
        if context is None:
            context = {}
        return OperationSerializer(context=context)

    def test_get_avoided_emissions_delegates_to_model(self):
        """Should delegate to instance.avoided_emissions property."""
        serializer = self._create_serializer()
        instance = Mock(spec=Operation)
        instance.avoided_emissions = 451.50

        result = serializer.get_avoided_emissions(instance)

        self.assertEqual(result, 451.50)

    def test_get_avoided_emissions_delegates_to_model_even_if_annotation_exists(self):
        """Should delegate avoided_emissions to model property."""
        serializer = self._create_serializer()
        instance = Mock()
        instance._avoided_emissions = 451.504
        instance.avoided_emissions = 0.0

        result = serializer.get_avoided_emissions(instance)

        self.assertEqual(result, 0.0)

    def test_get_energy_delegates_to_model_property(self):
        """Should use the energy property directly."""
        serializer = self._create_serializer()
        instance = Mock(spec=Operation)
        instance.energy = 72000.0

        result = serializer.get_energy(instance)

        self.assertEqual(result, 72000.0)


class OperationInputSerializerCreateTest(TestCase):
    """Tests for OperationInputSerializer.create() method."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
    ]

    def setUp(self):
        from core.models import Entity

        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        self.producer = Entity.objects.filter(entity_type=Entity.PRODUCER).first()
        self.depot = Depot.objects.first()
        self.production_site = ProductionSiteFactory.create(created_by=self.producer)
        self.biofuel_eth = Biocarburant.objects.get(code="ETH")
        self.feedstock_conv = MatierePremiere.biofuel.filter(category="CONV").first()

        self.mock_request = Mock()
        self.mock_request.entity.id = self.entity.id
        self.mock_request.unit = "l"

    @patch("tiruert.serializers.operation.OperationService")
    def test_create_calls_service_perform_checks(self, mock_service):
        """Should call OperationService.perform_checks_before_create()."""
        # Create real CarbureLot for FK constraint
        lot = CarbureLotFactory(
            volume=500,
            added_by=self.entity,
            carbure_producer=self.producer,
            carbure_production_site=self.production_site,
        )

        serializer = OperationInputSerializer(context={"request": self.mock_request})
        validated_data = {
            "type": Operation.CESSION,
            "customs_category": MatierePremiere.CONV,
            "biofuel": self.biofuel_eth,
            "debited_entity": self.entity,
            "credited_entity": self.entity,
            "to_depot": self.depot,
            "lots": [{"id": lot.id, "volume": 500}],
        }

        mock_service.perform_checks_before_create.return_value = None
        mock_service.define_operation_status.return_value = None
        mock_service.get_emission_rates_by_lot.return_value = {lot.id: 9.8}

        serializer.create(validated_data)

        mock_service.perform_checks_before_create.assert_called_once()
        call_args = mock_service.perform_checks_before_create.call_args[0]
        self.assertEqual(call_args[0], self.mock_request)
        self.assertEqual(call_args[1], self.entity.id)

    @patch("tiruert.serializers.operation.OperationService")
    def test_create_calls_service_define_status(self, mock_service):
        """Should call OperationService.define_operation_status()."""
        # Create real CarbureLot for FK constraint
        lot = CarbureLotFactory(
            volume=500,
            added_by=self.entity,
            carbure_producer=self.producer,
            carbure_production_site=self.production_site,
        )

        serializer = OperationInputSerializer(context={"request": self.mock_request})
        validated_data = {
            "type": Operation.CESSION,
            "customs_category": MatierePremiere.CONV,
            "biofuel": self.biofuel_eth,
            "debited_entity": self.entity,
            "credited_entity": self.entity,
            "to_depot": self.depot,
            "lots": [{"id": lot.id, "volume": 500}],
        }

        mock_service.perform_checks_before_create.return_value = None
        mock_service.define_operation_status.return_value = None
        mock_service.get_emission_rates_by_lot.return_value = {lot.id: 9.8}

        serializer.create(validated_data)

        mock_service.define_operation_status.assert_called_once_with(validated_data)

    @patch("tiruert.serializers.operation.OperationService.get_emission_rates_by_lot")
    @patch("tiruert.serializers.operation.OperationService.define_operation_status")
    @patch("tiruert.serializers.operation.OperationService.perform_checks_before_create")
    def test_create_creates_operation_and_details(
        self,
        _mock_perform_checks,
        _mock_define_operation_status,
        mock_get_emission_rates_by_lot,
    ):
        """Should create Operation and OperationDetails from lots."""
        # Create real CarbureLot for ForeignKey constraint
        lot = CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=self.feedstock_conv,
            biofuel=self.biofuel_eth,
            lot_status="ACCEPTED",
            volume=1000,
            ghg_total=9.8,
        )

        serializer = OperationInputSerializer(context={"request": self.mock_request})
        validated_data = {
            "type": Operation.CESSION,
            "customs_category": MatierePremiere.CONV,
            "biofuel": self.biofuel_eth,
            "debited_entity": self.entity,
            "credited_entity": self.entity,
            "to_depot": self.depot,
            "lots": [
                {"id": lot.id, "volume": 500},
                {"id": lot.id, "volume": 300},
            ],
        }

        mock_get_emission_rates_by_lot.return_value = {lot.id: 9.8}

        operation = serializer.create(validated_data)

        # Verify operation created
        self.assertIsNotNone(operation.id)
        self.assertEqual(operation.type, Operation.CESSION)
        self.assertEqual(operation.biofuel, self.biofuel_eth)

        # Verify details created
        self.assertEqual(operation.details.count(), 2)
        detail1 = operation.details.first()
        self.assertEqual(detail1.lot_id, lot.id)
        self.assertEqual(detail1.volume, 500)
        # emission_rate_per_mj comes from OperationService.get_emission_rates_by_lot
        self.assertEqual(detail1.emission_rate_per_mj, 9.8)

    def test_validate_type_accepts_authorized_types(self):
        """Should accept types in Operation.API_CREATABLE_TYPES."""
        serializer = OperationInputSerializer()

        # Only test the first one is enough, the whole list is tested in model tests
        result = serializer.validate_type(Operation.API_CREATABLE_TYPES[0])
        self.assertEqual(result, Operation.API_CREATABLE_TYPES[0])

    def test_validate_type_rejects_unauthorized_type(self):
        """Should reject operation types that cannot be created by the API."""
        serializer = OperationInputSerializer()

        with self.assertRaises(serializers.ValidationError):
            serializer.validate_type(Operation.CESSION)

    def test_objective_sector_invalid_on_non_teneur(self):
        """objective_sector must be rejected when type is not TENEUR."""
        serializer = OperationInputSerializer()
        data = {
            "type": Operation.TRANSFERT,
            "objective_sector": Operation.ESSENCE,
            "customs_category": "CONV",
            "biofuel": 1,
            "debited_entity": 1,
            "lots": [],
        }
        with self.assertRaises(Exception):
            serializer.validate(data)

    def test_objective_sector_accepted_on_teneur(self):
        """objective_sector must be accepted when type is TENEUR."""
        serializer = OperationInputSerializer()
        data = {
            "type": Operation.TENEUR,
            "objective_sector": Operation.ESSENCE,
        }
        result = serializer.validate(data)
        self.assertEqual(result["objective_sector"], Operation.ESSENCE)

    def test_objective_sector_optional_on_teneur(self):
        """objective_sector can be absent or None on a TENEUR operation."""
        serializer = OperationInputSerializer()
        data = {"type": Operation.TENEUR}
        result = serializer.validate(data)
        self.assertEqual(result, data)


class OperationUpdateSerializerTest(TestCase):
    """Tests for OperationUpdateSerializer field restrictions."""

    def test_only_allowed_fields_can_be_updated(self):
        """Should only allow updating 'to_depot' and 'status' fields."""
        serializer = OperationUpdateSerializer()
        allowed_fields = set(serializer.Meta.fields)

        self.assertEqual(allowed_fields, {"to_depot", "status"})


class OperationExcelRowSerializerTest(TestCase):
    """Tests for OperationExcelRowSerializer validation rules."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
    ]

    def setUp(self):
        from core.models import Entity

        self.entity = Entity.objects.create(
            name="TIRUERT Operator",
            entity_type=Entity.OPERATOR,
            is_enabled=True,
            is_tiruert_liable=True,
            accise_number="ACC-001",
        )
        self.biofuel_eth = Biocarburant.objects.get(code="ETH")
        self.feedstock_conv = MatierePremiere.biofuel.filter(category="CONV").first()
        self.lot = CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=self.feedstock_conv,
            biofuel=self.biofuel_eth,
            lot_status="ACCEPTED",
            volume=1000,
        )

    def test_transfert_requires_credited_entity(self):
        """TRANSFERT rows should require a credited entity."""
        serializer = OperationExcelRowSerializer()

        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate({"operation_type": Operation.TRANSFERT})

        self.assertEqual(
            context.exception.detail,
            {
                "credited_entity": serializers.ErrorDetail(
                    string="Destinataire requis pour les opérations de type TRANSFERT.",
                    code="invalid",
                )
            },
        )

    def test_operation_type_is_normalized_and_validated(self):
        """Operation type should be normalized to uppercase and validated."""
        serializer = OperationExcelRowSerializer()

        self.assertEqual(serializer.validate_operation_type(" transfert "), Operation.TRANSFERT)
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_operation_type("invalid")

    def test_volume_must_be_positive(self):
        """Volume should be strictly greater than zero."""
        serializer = OperationExcelRowSerializer()

        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate_volume(0)

        self.assertEqual(
            context.exception.detail,
            ["La valeur du volume doit être supérieure à zéro."],
        )

    def test_serializer_validates_transfert_row(self):
        """A valid TRANSFERT row should resolve related objects correctly."""
        serializer = OperationExcelRowSerializer(
            data={
                "lot_id": self.lot.id,
                "volume": 125.5,
                "operation_type": " transfert ",
                "credited_entity": self.entity.id,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["operation_type"], Operation.TRANSFERT)
        self.assertEqual(serializer.validated_data["credited_entity"], self.entity)
        self.assertEqual(serializer.validated_data["lot_id"], self.lot)


class OperationCorrectionSerializerUpdateTest(TestCase):
    """Tests for OperationCorrectionSerializer.update() correction logic."""

    pass
