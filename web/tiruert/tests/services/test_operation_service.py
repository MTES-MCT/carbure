"""
Unit tests for OperationService methods.

Tests the business logic in OperationService, particularly create_operations_from_lots.
"""

from django.test import TestCase

from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere
from tiruert.models import Operation
from tiruert.services.operation import OperationService
from transactions.factories import CarbureLotFactory
from transactions.models import Depot


class OperationServiceTestCase(TestCase):
    """Base test case with fixtures for OperationService tests."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/depots.json",
        "json/entities_sites.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Create test data once for the entire test class."""
        # Get references from fixtures
        cls.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        cls.depot = Depot.objects.first()
        cls.feedstock_conv = MatierePremiere.objects.filter(category="CONV").first()
        cls.feedstock_ann_ix_a = MatierePremiere.objects.filter(category="ANN-IX-A").first()
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
