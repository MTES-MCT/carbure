from unittest.mock import Mock, patch

from django.test import TestCase

from core.models import Biocarburant, MatierePremiere
from tiruert.models import Operation
from tiruert.serializers import OperationListSerializer, OperationSerializer
from tiruert.serializers.operation import (
    BaseOperationSerializer,
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

    def test_get_volume_l_delegates_to_model(self):
        """Should delegate to instance.volume_l property."""
        serializer = self._create_serializer()
        instance = Mock(spec=Operation)
        instance.volume_l = 1500.0

        result = serializer.get_volume_l(instance)

        self.assertEqual(result, 1500.0)

    def test_get_quantity_delegates_to_model_with_unit(self):
        """Should delegate to instance.quantity(unit) with unit from context."""
        serializer = self._create_serializer(context={"unit": "mj"})
        instance = Mock(spec=Operation)
        instance.quantity = Mock(return_value=36000.0)

        result = serializer.get_quantity(instance)

        instance.quantity.assert_called_once_with(unit="mj")
        self.assertEqual(result, 36000.0)

    def test_get_unit_returns_unit_from_context(self):
        """Should return unit from context."""
        serializer = self._create_serializer(context={"unit": "kg"})
        instance = Mock(spec=Operation)

        result = serializer.get_unit(instance)

        self.assertEqual(result, "kg")

    def test_get_fields_removes_details_when_not_requested(self):
        """Should not build the nested details field on list responses by default."""
        serializer = OperationListSerializer(context={"details": False})

        self.assertNotIn("details", serializer.fields)

    def test_get_fields_keeps_details_when_requested(self):
        """Should keep nested details field when explicit details mode is enabled."""
        serializer = OperationListSerializer(context={"details": True})

        self.assertIn("details", serializer.fields)

    def test_operation_list_serializer_uses_annotated_quantity_and_avoided_emissions(self):
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
        operation._quantity = 123.456
        operation._avoided_emissions = 78.901
        operation.declaration_year = 2024

        serializer = OperationListSerializer(operation, context={"details": False, "unit": "l"})

        self.assertEqual(serializer.data["quantity"], 123.46)
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

    def test_get_avoided_emissions_uses_annotation_when_available(self):
        """Should prefer annotated avoided emissions on list querysets."""
        serializer = self._create_serializer()
        instance = Mock(spec=Operation)
        instance._avoided_emissions = 451.504

        result = serializer.get_avoided_emissions(instance)

        self.assertEqual(result, 451.5)

    def test_get_quantity_mj_always_uses_mj_unit(self):
        """Should always use 'mj' unit regardless of context unit."""
        # Test with different context units to ensure mj is always used
        for context_unit in ["l", "kg", "mj"]:
            with self.subTest(context_unit=context_unit):
                serializer = self._create_serializer(context={"unit": context_unit})
                instance = Mock(spec=Operation)
                instance.quantity = Mock(return_value=72000.0)

                result = serializer.get_quantity_mj(instance)

                # Should always call with "mj" regardless of context
                instance.quantity.assert_called_once_with(unit="mj", force=True)
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

    @patch("tiruert.serializers.operation.OperationService")
    def test_create_creates_operation_and_details(self, mock_service):
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

        mock_service.perform_checks_before_create.return_value = None
        mock_service.define_operation_status.return_value = None
        mock_service.get_emission_rates_by_lot.return_value = {lot.id: 9.8}

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


class OperationCorrectionSerializerUpdateTest(TestCase):
    """Tests for OperationCorrectionSerializer.update() correction logic."""

    pass
