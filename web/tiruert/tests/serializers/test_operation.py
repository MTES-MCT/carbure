from unittest.mock import Mock, patch

from django.test import TestCase

from core.models import Biocarburant, MatierePremiere
from tiruert.models import Operation
from tiruert.serializers import OperationSerializer
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
            "lots": [{"id": lot.id, "volume": 500, "emission_rate_per_mj": 10.5}],
        }

        mock_service.perform_checks_before_create.return_value = None
        mock_service.define_operation_status.return_value = None

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
            "lots": [{"id": lot.id, "volume": 500, "emission_rate_per_mj": 10.5}],
        }

        mock_service.perform_checks_before_create.return_value = None
        mock_service.define_operation_status.return_value = None

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
                {"id": lot.id, "volume": 500, "emission_rate_per_mj": 10.5},
                {"id": lot.id, "volume": 300, "emission_rate_per_mj": 12.3},
            ],
        }

        mock_service.perform_checks_before_create.return_value = None
        mock_service.define_operation_status.return_value = None

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
        self.assertEqual(detail1.emission_rate_per_mj, 10.5)

    def test_validate_type_accepts_authorized_types(self):
        """Should accept types in Operation.API_CREATABLE_TYPES."""
        serializer = OperationInputSerializer()

        # Only test the first one is enough, the whole list is tested in model tests
        result = serializer.validate_type(Operation.API_CREATABLE_TYPES[0])
        self.assertEqual(result, Operation.API_CREATABLE_TYPES[0])


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
