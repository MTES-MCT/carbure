from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere
from tiruert.models import Operation
from tiruert.services.operation import OperationService, OperationServiceErrors
from transactions.factories import CarbureLotFactory
from transactions.models import Depot


class OperationServiceTestCase(TestCase):
    """Base test case with fixtures for OperationService tests."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Create test data once for the entire test class."""
        # Get references from fixtures
        cls.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        cls.depot = Depot.objects.first()
        cls.feedstock_conv = MatierePremiere.biofuel.filter(category="CONV").first()
        cls.feedstock_ann_ix_a = MatierePremiere.biofuel.filter(category="ANN-IX-A").first()
        cls.biofuel_eth = Biocarburant.objects.get(code="ETH")
        cls.biofuel_emag = Biocarburant.objects.get(code="EMAG")

        # Create valid lots that will generate TIRUERT operations
        cls.lot_blending_frozen = CarbureLotFactory.create(
            carbure_client=cls.entity,
            feedstock=cls.feedstock_conv,
            biofuel=cls.biofuel_eth,
            lot_status="FROZEN",
            delivery_type="BLENDING",
            volume=1000,
            ghg_total=1.3,
            carbure_delivery_site=cls.depot,
        )

        cls.lot_blending_accepted = CarbureLotFactory.create(
            carbure_client=cls.entity,
            feedstock=cls.feedstock_conv,
            biofuel=cls.biofuel_eth,
            lot_status="ACCEPTED",
            delivery_type="BLENDING",
            volume=2000,
            ghg_total=2.5,
            carbure_delivery_site=cls.depot,
        )

        cls.lot_direct = CarbureLotFactory.create(
            carbure_client=cls.entity,
            feedstock=cls.feedstock_conv,
            biofuel=cls.biofuel_eth,
            lot_status="ACCEPTED",
            delivery_type="DIRECT",
            volume=3000,
            ghg_total=3.4,
            carbure_delivery_site=cls.depot,
        )

        cls.lot_rfc_eth = CarbureLotFactory.create(
            carbure_client=cls.entity,
            feedstock=cls.feedstock_conv,
            biofuel=cls.biofuel_eth,
            lot_status="ACCEPTED",
            delivery_type="RFC",
            volume=4000,
            ghg_total=4.8,
            carbure_delivery_site=cls.depot,
        )

        cls.lot_rfc_emag = CarbureLotFactory.create(
            carbure_client=cls.entity,
            feedstock=cls.feedstock_ann_ix_a,
            biofuel=cls.biofuel_emag,
            lot_status="ACCEPTED",
            delivery_type="RFC",
            volume=5000,
            ghg_total=5.6,
            carbure_delivery_site=cls.depot,
        )

        # Create invalid lots (won't generate operations)
        cls.lot_draft = CarbureLotFactory.create(
            carbure_client=cls.entity,
            feedstock=cls.feedstock_conv,
            biofuel=cls.biofuel_eth,
            lot_status="DRAFT",
            delivery_type="BLENDING",
            volume=1000,
            carbure_delivery_site=cls.depot,
        )

        cls.lot_export = CarbureLotFactory.create(
            carbure_client=cls.entity,
            feedstock=cls.feedstock_ann_ix_a,
            biofuel=cls.biofuel_emag,
            lot_status="ACCEPTED",
            delivery_type="EXPORT",
            volume=1000,
            carbure_delivery_site=cls.depot,
        )

        cls.entity_lots = CarbureLot.objects.filter(carbure_client=cls.entity)


class OperationServiceCreateOperationsTest(OperationServiceTestCase):
    """Test OperationService.create_operations_from_lots() method."""

    def test_create_operations_from_lots_creates_correct_number(self):
        """Should create 4 operations from 5 valid lots (grouped by type/feedstock/biofuel/depot)."""
        OperationService.create_operations_from_lots(self.entity_lots)

        operations = Operation.objects.all()
        self.assertEqual(operations.count(), 4)

    def test_create_operations_from_lots_groups_correctly(self):
        """Should group lots by delivery_type, feedstock category, biofuel and depot."""
        OperationService.create_operations_from_lots(self.entity_lots)

        # Check BLENDING operations (2 lots → 1 operation INCORPORATION)
        incorporation_ops = Operation.objects.filter(type=Operation.INCORPORATION)
        self.assertEqual(incorporation_ops.count(), 1)
        incorporation = incorporation_ops.first()
        self.assertEqual(incorporation.details.count(), 2)

        # Check DIRECT operations (1 lot → 1 operation LIVRAISON_DIRECTE)
        livraison_ops = Operation.objects.filter(type=Operation.LIVRAISON_DIRECTE)
        self.assertEqual(livraison_ops.count(), 1)
        self.assertEqual(livraison_ops.first().details.count(), 1)

        # Check RFC operations (2 lots → 2 operations MAC_BIO, different biofuels)
        mac_bio_ops = Operation.objects.filter(type=Operation.MAC_BIO)
        self.assertEqual(mac_bio_ops.count(), 2)

    def test_create_operations_from_lots_sets_validated_status(self):
        """Should set status to VALIDATED for all created operations."""
        OperationService.create_operations_from_lots(self.entity_lots)

        operations = Operation.objects.all()
        for operation in operations:
            self.assertEqual(operation.status, Operation.VALIDATED)

    def test_create_operations_from_lots_avoids_duplicates(self):
        """Should not create operations for lots that already have operations."""
        # First call creates operations
        OperationService.create_operations_from_lots(self.entity_lots)
        first_count = Operation.objects.count()

        # Second call should not create duplicates
        OperationService.create_operations_from_lots(self.entity_lots)
        second_count = Operation.objects.count()

        self.assertEqual(first_count, second_count)

    def test_create_operations_from_lots_sets_correct_attributes(self):
        """Should set correct attributes on created operations."""
        OperationService.create_operations_from_lots(self.entity_lots)

        operation = Operation.objects.first()

        # Check attributes from first lot in group
        self.assertEqual(operation.credited_entity, self.entity)
        self.assertIsNone(operation.debited_entity)
        self.assertIsNone(operation.from_depot)
        self.assertEqual(operation.to_depot, self.depot)
        self.assertIsNotNone(operation.biofuel)
        self.assertIsNotNone(operation.customs_category)


class OperationServiceFilterLotsTest(OperationServiceTestCase):
    """Test OperationService.filter_valid_lots() method."""

    def test_filter_valid_lots_returns_only_valid_lots(self):
        """Should return exactly the 5 valid lots (ACCEPTED/FROZEN + RFC/BLENDING/DIRECT)."""
        valid_lots = OperationService.filter_valid_lots(self.entity_lots)

        # Should return exactly 5 valid lots
        self.assertEqual(valid_lots.count(), 5)

        # Verify all returned lots have valid status
        for lot in valid_lots:
            self.assertIn(lot.lot_status, ["ACCEPTED", "FROZEN"])

        # Verify all returned lots have valid delivery_type
        for lot in valid_lots:
            self.assertIn(lot.delivery_type, ["RFC", "BLENDING", "DIRECT"])


class OperationServiceRemoveExistingLotsTest(OperationServiceTestCase):
    """Test OperationService.remove_existing_lots() method."""

    def test_remove_existing_lots_removes_lots_with_operations(self):
        """Should remove lots that already have operations."""
        # Create operations from valid lots
        OperationService.create_operations_from_lots(self.entity_lots)

        # Get valid lots
        valid_lots = OperationService.filter_valid_lots(self.entity_lots)

        # Remove existing lots
        remaining_lots = OperationService.remove_existing_lots(valid_lots)

        # Should be empty since all valid lots now have operations
        self.assertEqual(remaining_lots.count(), 0)

    def test_remove_existing_lots_keeps_lots_without_operations(self):
        """Should keep lots that don't have operations yet."""
        # Get valid lots
        valid_lots = OperationService.filter_valid_lots(self.entity_lots)

        # Remove existing lots (none should be removed)
        remaining_lots = OperationService.remove_existing_lots(valid_lots)

        # Should keep all 5 valid lots
        self.assertEqual(remaining_lots.count(), 5)


class OperationServiceCheckDebitedEntityTest(TestCase):
    """Test OperationService.check_debited_entity() validation."""

    def test_check_debited_entity_passes_when_ids_match(self):
        """Should pass silently when debited_entity.id matches entity_id."""
        entity = Mock()
        entity.id = 42

        data = {"debited_entity": entity}

        # Should not raise exception
        OperationService.check_debited_entity(entity_id=42, data=data)

    def test_check_debited_entity_raises_error_when_ids_dont_match(self):
        """Should raise ValidationError when debited_entity.id != entity_id."""
        entity = Mock()
        entity.id = 42

        data = {"debited_entity": entity}

        with self.assertRaises(ValidationError) as context:
            OperationService.check_debited_entity(entity_id=99, data=data)

        self.assertIn("debited_entity", context.exception.detail)
        self.assertIn(
            OperationServiceErrors.ENTITY_ID_DO_NOT_MATCH_DEBITED_ID,
            str(context.exception.detail["debited_entity"]),
        )


class OperationServiceCheckVolumesTest(TestCase):
    """Test OperationService.check_volumes() validation with mocks."""

    @patch("tiruert.services.operation.TeneurService.prepare_data")
    def test_check_volumes_passes_when_volumes_sufficient(self, mock_prepare_data):
        """Should pass when requested volumes are available."""
        # Mock TeneurService.prepare_data to return available volumes
        mock_prepare_data.return_value = (
            [1000.0, 2000.0],  # np_volumes (available)
            None,
            [1, 2],  # np_lot_ids
            None,
            None,
        )

        selected_lots = [
            {"id": 1, "volume": 500},  # Request 500 out of 1000 available
            {"id": 2, "volume": 1500},  # Request 1500 out of 2000 available
        ]

        data = {"biofuel": Mock()}
        unit = "l"

        # Should not raise exception
        OperationService.check_volumes(selected_lots, data, unit)
        mock_prepare_data.assert_called_once_with(data, unit)

    @patch("tiruert.services.operation.TeneurService.prepare_data")
    def test_check_volumes_raises_error_when_lot_not_found(self, mock_prepare_data):
        """Should raise ValidationError when requested lot_id doesn't exist."""
        # Mock TeneurService.prepare_data with only lot_id=1 available
        mock_prepare_data.return_value = (
            [1000.0],  # np_volumes
            None,
            [1],  # np_lot_ids (only lot 1 exists)
            None,
            None,
        )

        selected_lots = [
            {"id": 999, "volume": 500},  # Request non-existent lot
        ]

        data = {"biofuel": Mock()}
        unit = "l"

        with self.assertRaises(ValidationError) as context:
            OperationService.check_volumes(selected_lots, data, unit)

        self.assertIn("lot_id: 999", context.exception.detail)
        self.assertIn(
            OperationServiceErrors.LOT_NOT_FOUND,
            str(context.exception.detail["lot_id: 999"]),
        )

    @patch("tiruert.services.operation.TeneurService.prepare_data")
    def test_check_volumes_raises_error_when_insufficient_volume(self, mock_prepare_data):
        """Should raise ValidationError when requested volume exceeds available."""
        # Mock TeneurService.prepare_data with 1000L available
        mock_prepare_data.return_value = (
            [1000.0],  # np_volumes (available)
            None,
            [1],  # np_lot_ids
            None,
            None,
        )

        selected_lots = [
            {"id": 1, "volume": 1500},  # Request 1500L but only 1000L available
        ]

        data = {"biofuel": Mock()}
        unit = "l"

        with self.assertRaises(ValidationError) as context:
            OperationService.check_volumes(selected_lots, data, unit)

        self.assertIn("lot_id: 1", context.exception.detail)
        self.assertIn(
            OperationServiceErrors.INSUFFICIENT_INPUT_VOLUME,
            str(context.exception.detail["lot_id: 1"]),
        )


class OperationServiceCheckObjectivesComplianceTest(TestCase):
    """Test OperationService.check_objectives_compliance() validation with mocks."""

    @patch("tiruert.services.operation.ObjectiveService.calculate_target_for_specific_category")
    def test_check_objectives_compliance_passes_when_no_target(self, mock_calculate_target):
        """Should pass when target is None (no objective or already reached)."""
        mock_calculate_target.return_value = None

        mock_request = Mock()
        mock_request.entity.id = 1
        mock_request.GET = {}

        data = {"type": Operation.TENEUR, "customs_category": "CONV", "biofuel": Mock(code="ETH")}
        selected_lots = []
        entity_id = 1

        # Should not raise exception (no target = no check)
        OperationService.check_objectives_compliance(mock_request, selected_lots, data, entity_id)

    @patch("tiruert.services.operation.CarbureLot")
    @patch("tiruert.services.operation.BalanceService.calculate_balance")
    @patch("tiruert.services.operation.ObjectiveService.calculate_target_for_specific_category")
    def test_check_services_method_are_called_with_data(
        self, mock_calculate_target, mock_calculate_balance, mock_carbure_lot
    ):
        """Should call ObjectiveService and BalanceService with correct parameters (MJ unit)."""
        mock_calculate_target.return_value = 100000  # Dummy target
        mock_calculate_balance.return_value = {"balance_key": {"pending_teneur": 0, "declared_teneur": 0}}

        # Mock CarbureLot.objects.get to return a lot with pci_litre
        mock_lot = Mock()
        mock_lot.biofuel.pci_litre = 21.3
        mock_carbure_lot.objects.get.return_value = mock_lot

        mock_request = Mock()
        mock_request.entity.id = 1
        mock_request.GET = {}

        data = {"type": Operation.TENEUR, "customs_category": "CONV", "biofuel": Mock(code="ETH")}
        selected_lots = [{"id": 1, "volume": 1000}]
        entity_id = 1

        # Call the method
        OperationService.check_objectives_compliance(mock_request, selected_lots, data, entity_id)

        # Verify ObjectiveService called with correct parameters
        mock_calculate_target.assert_called_once_with("CONV", 1)

        # Verify BalanceService called with correct parameters
        mock_calculate_balance.assert_called_once()
        called_args = mock_calculate_balance.call_args[0]
        self.assertEqual(called_args[1], 1)  # entity_id
        self.assertEqual(called_args[2], None)  # depot_id
        self.assertEqual(called_args[3], "mj")  # unit

    @patch("tiruert.services.operation.CarbureLot")
    @patch("tiruert.services.operation.BalanceService.calculate_balance")
    @patch("tiruert.services.operation.ObjectiveService.calculate_target_for_specific_category")
    def test_check_objectives_compliance_passes_when_below_target(
        self, mock_calculate_target, mock_calculate_balance, mock_carbure_lot
    ):
        """Should pass when future teneur is below target."""
        # Target = 100,000 MJ
        mock_calculate_target.return_value = 100000

        # Current balance: 50,000 MJ pending + 20,000 MJ declared
        mock_calculate_balance.return_value = {"balance_key": {"pending_teneur": 50000, "declared_teneur": 20000}}

        # Mock CarbureLot with pci_litre = 10 MJ/L
        mock_lot = Mock()
        mock_lot.biofuel.pci_litre = 10
        mock_carbure_lot.objects.get.return_value = mock_lot

        mock_request = Mock()
        mock_request.entity.id = 1
        mock_request.GET = {}

        data = {"type": Operation.TENEUR, "customs_category": "CONV", "biofuel": Mock(code="ETH")}

        # Request to add 1000L = 10,000 MJ
        # Future teneur: 50,000 + 20,000 + 10,000 = 80,000 MJ < 100,000 (OK)
        selected_lots = [{"id": 1, "volume": 1000}]
        entity_id = 1

        # Should not raise exception
        OperationService.check_objectives_compliance(mock_request, selected_lots, data, entity_id)

    @patch("tiruert.services.operation.CarbureLot")
    @patch("tiruert.services.operation.BalanceService.calculate_balance")
    @patch("tiruert.services.operation.ObjectiveService.calculate_target_for_specific_category")
    def test_check_objectives_compliance_raises_error_when_exceeds_target(
        self, mock_calculate_target, mock_calculate_balance, mock_carbure_lot
    ):
        """Should raise ValidationError when future teneur exceeds target."""
        # Target = 100,000 MJ
        mock_calculate_target.return_value = 100000

        # Current balance: 80,000 MJ pending + 15,000 MJ declared
        mock_calculate_balance.return_value = {"balance_key": {"pending_teneur": 80000, "declared_teneur": 15000}}

        # Mock CarbureLot with pci_litre = 10 MJ/L
        mock_lot = Mock()
        mock_lot.biofuel.pci_litre = 10
        mock_carbure_lot.objects.get.return_value = mock_lot

        mock_request = Mock()
        mock_request.entity.id = 1
        mock_request.GET = {}

        data = {"type": Operation.TENEUR, "customs_category": "CONV", "biofuel": Mock(code="ETH")}

        # Request to add 2000L = 20,000 MJ
        # Future teneur: 80,000 + 15,000 + 20,000 = 115,000 MJ > 100,000 (ERROR)
        selected_lots = [{"id": 1, "volume": 2000}]
        entity_id = 1

        with self.assertRaises(ValidationError) as context:
            OperationService.check_objectives_compliance(mock_request, selected_lots, data, entity_id)

        error_key = list(context.exception.detail.keys())[0]
        self.assertIn("futur_teneur", error_key)
        self.assertIn("target", error_key)
        self.assertIn(
            OperationServiceErrors.TARGET_EXCEEDED,
            str(context.exception.detail[error_key]),
        )

    def test_check_objectives_compliance_skips_for_non_teneur_operations(self):
        """Should skip check for non-TENEUR operation types."""
        mock_request = Mock()
        data = {"type": Operation.CESSION}  # Not TENEUR
        selected_lots = []
        entity_id = 1

        # Should not raise exception (early return for non-TENEUR)
        OperationService.check_objectives_compliance(mock_request, selected_lots, data, entity_id)


class OperationServiceProcessEP2LotsTest(TestCase):
    """Test OperationService.process_ep2_lots() split logic."""

    fixtures = ["json/biofuels.json", "json/feedstock.json"]

    def test_process_ep2_lots_splits_ep2_correctly(self):
        """Should split EP2 lot into 40% CONV + 60% EP2AM."""
        feedstock_ep2 = MatierePremiere.biofuel.get(code="EP2")
        biofuel_eth = Biocarburant.objects.get(code="ETH")

        lot_ep2 = Mock()
        lot_ep2.feedstock = feedstock_ep2
        lot_ep2.biofuel = biofuel_eth
        lot_ep2.volume = 1000.0

        result_lots = OperationService.process_ep2_lots([lot_ep2])

        # Should return 2 lots
        self.assertEqual(len(result_lots), 2)

        # First lot: 40% CONV
        conv_lot = result_lots[0]
        self.assertEqual(conv_lot.feedstock.category, MatierePremiere.CONV)
        self.assertEqual(conv_lot.volume, 400.0)

        # Second lot: 60% EP2AM
        ep2am_lot = result_lots[1]
        self.assertEqual(ep2am_lot.feedstock.category, MatierePremiere.EP2AM)
        self.assertEqual(ep2am_lot.volume, 600.0)

    def test_process_ep2_lots_keeps_non_ep2_unchanged(self):
        """Should keep non-EP2 lots unchanged."""
        feedstock_conv = MatierePremiere.biofuel.filter(category="CONV").first()
        biofuel_eth = Biocarburant.objects.get(code="ETH")

        lot_conv = Mock()
        lot_conv.feedstock = feedstock_conv
        lot_conv.biofuel = biofuel_eth
        lot_conv.volume = 1000.0

        result_lots = OperationService.process_ep2_lots([lot_conv])

        # Should return 1 unchanged lot
        self.assertEqual(len(result_lots), 1)
        self.assertEqual(result_lots[0], lot_conv)
        self.assertEqual(result_lots[0].volume, 1000.0)

    def test_process_ep2_lots_handles_mixed_lots(self):
        """Should correctly process mix of EP2 and non-EP2 lots."""
        feedstock_ep2 = MatierePremiere.biofuel.get(code="EP2")
        feedstock_conv = MatierePremiere.biofuel.filter(category="CONV").first()

        lot_ep2 = Mock()
        lot_ep2.feedstock = feedstock_ep2
        lot_ep2.volume = 1000.0

        lot_conv = Mock()
        lot_conv.feedstock = feedstock_conv
        lot_conv.volume = 500.0

        result_lots = OperationService.process_ep2_lots([lot_ep2, lot_conv])

        # Should return 3 lots: 2 from EP2 split + 1 unchanged CONV
        self.assertEqual(len(result_lots), 3)
