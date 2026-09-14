from unittest.mock import Mock, patch

from django.http import QueryDict
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere, Pays
from tiruert.models import Operation, OperationDetail
from tiruert.services.operation import OperationService, OperationServiceErrors
from transactions.factories import CarbureLotFactory
from transactions.factories.depot import DepotFactory
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
            usage=CarbureLot.USAGE_ROAD,
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
            usage=CarbureLot.USAGE_AGRICULTURE,
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


class OperationServiceEmissionRatesTest(OperationServiceTestCase):
    def test_get_emission_rates_by_lot_returns_oldest_detail_per_lot(self):
        lot = self.lot_blending_accepted

        first_operation = Operation.objects.create(
            type=Operation.CESSION,
            status=Operation.VALIDATED,
            customs_category=lot.feedstock.category,
            biofuel=lot.biofuel,
            credited_entity=self.entity,
            debited_entity=self.entity,
        )
        OperationDetail.objects.create(
            operation=first_operation,
            lot=lot,
            volume=100.0,
            emission_rate_per_mj=1.1,
        )

        second_operation = Operation.objects.create(
            type=Operation.CESSION,
            status=Operation.VALIDATED,
            customs_category=lot.feedstock.category,
            biofuel=lot.biofuel,
            credited_entity=self.entity,
            debited_entity=self.entity,
        )
        OperationDetail.objects.create(
            operation=second_operation,
            lot=lot,
            volume=100.0,
            emission_rate_per_mj=2.2,
        )

        rates_by_lot = OperationService.get_emission_rates_by_lot([lot.id])

        self.assertEqual(rates_by_lot, {lot.id: 1.1})

    def test_get_emission_rates_by_lot_raises_all_missing_lot_ids(self):
        with self.assertRaises(ValidationError) as context:
            OperationService.get_emission_rates_by_lot([999001, 999002])

        self.assertEqual(
            context.exception.detail,
            {
                "lot_id: 999001": OperationServiceErrors.LOT_EMISSION_RATE_NOT_FOUND,
                "lot_id: 999002": OperationServiceErrors.LOT_EMISSION_RATE_NOT_FOUND,
            },
        )


class OperationServiceCreateOperationsTest(OperationServiceTestCase):
    """Test OperationService.create_operations_from_lots() method."""

    @patch("tiruert.services.operation.OperationService.convert_emag_lots")
    @patch("tiruert.services.operation.OperationService.calculate_volume_ethanol_15")
    @patch("tiruert.services.operation.OperationService.process_ep2_lots")
    @patch("tiruert.services.operation.OperationService.remove_existing_lots")
    @patch("tiruert.services.operation.OperationService.filter_fr_delivery_site")
    @patch("tiruert.services.operation.OperationService.filter_valid_lots")
    def test_create_operations_from_lots_calls_filter_and_transform_steps(
        self,
        mock_filter_valid_lots,
        mock_filter_fr_delivery_site,
        mock_remove_existing_lots,
        mock_process_ep2_lots,
        mock_calculate_volume_ethanol_15,
        mock_convert_emag_lots,
    ):
        """Should call the 3 lot filters and 3 transformation methods in order."""
        input_lots = Mock(name="input_lots")
        lots_after_valid_filter = Mock(name="lots_after_valid_filter")
        lots_after_fr_filter = Mock(name="lots_after_fr_filter")
        lots_after_existing_filter = [Mock(name="lot")]
        lots_after_ep2 = []

        mock_filter_valid_lots.return_value = lots_after_valid_filter
        mock_filter_fr_delivery_site.return_value = lots_after_fr_filter
        mock_remove_existing_lots.return_value = lots_after_existing_filter
        mock_process_ep2_lots.return_value = lots_after_ep2
        mock_calculate_volume_ethanol_15.return_value = None
        mock_convert_emag_lots.return_value = None

        OperationService.create_operations_from_lots(input_lots)

        mock_filter_valid_lots.assert_called_once_with(input_lots)
        mock_filter_fr_delivery_site.assert_called_once_with(lots_after_valid_filter)
        mock_remove_existing_lots.assert_called_once_with(lots_after_fr_filter)
        mock_process_ep2_lots.assert_called_once_with(lots_after_existing_filter)
        mock_calculate_volume_ethanol_15.assert_called_once_with(lots_after_ep2)
        mock_convert_emag_lots.assert_called_once_with(lots_after_ep2)

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

    # TODO: Re-enable when status logic is implemented
    # def test_create_operations_from_lots_sets_validated_status(self):
    #     """Should set status to VALIDATED for all created operations."""
    #     OperationService.create_operations_from_lots(self.entity_lots)

    #     operations = Operation.objects.all()
    #     for operation in operations:
    #         self.assertEqual(operation.status, Operation.VALIDATED)

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
        """Should apply RFC usage whitelist while still allowing empty RFC usage."""
        excluded_rfc = CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=self.feedstock_conv,
            biofuel=self.biofuel_eth,
            lot_status="ACCEPTED",
            delivery_type="RFC",
            usage=CarbureLot.USAGE_HEATING,
            volume=700,
            carbure_delivery_site=self.depot,
        )
        included_rfc_empty_usage = CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=self.feedstock_conv,
            biofuel=self.biofuel_eth,
            lot_status="ACCEPTED",
            delivery_type="RFC",
            usage="",
            volume=680,
            carbure_delivery_site=self.depot,
        )
        included_blending = CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=self.feedstock_conv,
            biofuel=self.biofuel_eth,
            lot_status="ACCEPTED",
            delivery_type="BLENDING",
            usage=CarbureLot.USAGE_HEATING,
            volume=650,
            carbure_delivery_site=self.depot,
        )

        valid_lots = OperationService.filter_valid_lots(self.entity_lots)

        # 5 initial valid lots + 1 RFC lot with empty usage + 1 blending lot with non-whitelisted usage.
        self.assertEqual(valid_lots.count(), 7)
        self.assertNotIn(excluded_rfc.id, valid_lots.values_list("id", flat=True))
        self.assertIn(included_rfc_empty_usage.id, valid_lots.values_list("id", flat=True))
        self.assertIn(included_blending.id, valid_lots.values_list("id", flat=True))

        # Verify all returned lots have valid status
        for lot in valid_lots:
            self.assertIn(lot.lot_status, ["ACCEPTED", "FROZEN"])

        # Verify all returned lots have valid delivery_type
        for lot in valid_lots:
            self.assertIn(lot.delivery_type, ["RFC", "BLENDING", "DIRECT"])

        # Verify RFC-specific usage whitelist constraint
        for lot in valid_lots.filter(delivery_type="RFC"):
            self.assertIn(
                lot.usage,
                [
                    "",
                    CarbureLot.USAGE_ROAD,
                    CarbureLot.USAGE_AGRICULTURE,
                    CarbureLot.USAGE_CONSTRUCTION,
                    CarbureLot.USAGE_MARITIME,
                    CarbureLot.USAGE_INLAND_WATERWAY,
                    CarbureLot.USAGE_RAIL,
                ],
            )

    def test_filter_fr_delivery_site_keeps_fr_and_no_delivery_site_lots(self):
        """Should keep lots with a FR delivery site and lots with no delivery site."""
        non_fr_depot = DepotFactory(country=Pays.objects.get(code_pays="DE"))

        lot_non_fr = CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=self.feedstock_conv,
            biofuel=self.biofuel_eth,
            lot_status="ACCEPTED",
            delivery_type="BLENDING",
            volume=900,
            carbure_delivery_site=non_fr_depot,
        )

        lot_without_delivery_site = CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=self.feedstock_conv,
            biofuel=self.biofuel_eth,
            lot_status="ACCEPTED",
            delivery_type="BLENDING",
            volume=800,
            carbure_delivery_site=None,
        )

        lots = CarbureLot.objects.filter(
            id__in=[
                self.lot_blending_accepted.id,
                lot_non_fr.id,
                lot_without_delivery_site.id,
            ]
        )
        filtered_lots = OperationService.filter_fr_delivery_site(lots)

        self.assertEqual(filtered_lots.count(), 2)
        self.assertSetEqual(
            set(filtered_lots.values_list("id", flat=True)),
            {self.lot_blending_accepted.id, lot_without_delivery_site.id},
        )


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
        # Should not raise exception
        OperationService.check_volumes(selected_lots, data)
        mock_prepare_data.assert_called_once_with(data)

    @patch("tiruert.services.operation.TeneurService.prepare_data")
    def test_check_volumes_raises_error_when_lot_not_found(self, mock_prepare_data):
        """Should raise ValidationError when requested lot_id doesn't exist."""
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
        with self.assertRaises(ValidationError) as context:
            OperationService.check_volumes(selected_lots, data)

        self.assertIn("lot_id", context.exception.detail.keys())
        self.assertIn("999: Ce lot n'a pas de volume disponible", str(context.exception.detail.values()))

    @patch("tiruert.services.operation.TeneurService.prepare_data")
    def test_check_volumes_raises_error_when_insufficient_volume(self, mock_prepare_data):
        """Should raise ValidationError when requested volume exceeds available."""
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
        with self.assertRaises(ValidationError) as context:
            OperationService.check_volumes(selected_lots, data)

        self.assertIn("volume", context.exception.detail.keys())
        self.assertIn("1 : Volume insuffisant pour ce lot", str(context.exception.detail.values()))

    @patch("tiruert.services.operation.TeneurService.prepare_data")
    def test_check_volumes_raises_error_when_duplicate_lot_total_exceeds_available(self, mock_prepare_data):
        """Should raise ValidationError when duplicate lot lines exceed available volume once aggregated."""
        mock_prepare_data.return_value = (
            [1000.0],  # np_volumes (available)
            None,
            [1],  # np_lot_ids
            None,
            None,
        )

        selected_lots = [
            {"id": 1, "volume": 700},
            {"id": 1, "volume": 400},  # Total requested = 1100 > 1000 available
        ]

        data = {"biofuel": Mock()}

        with self.assertRaises(ValidationError) as context:
            OperationService.check_volumes(selected_lots, data)

        self.assertIn("volume", context.exception.detail.keys())
        self.assertIn("1 : Volume insuffisant pour ce lot", str(context.exception.detail.values()))


class OperationServiceCheckObjectivesComplianceTest(TestCase):
    """Test OperationService.check_objectives_compliance() validation with mocks."""

    @patch("tiruert.services.operation.ObjectiveService.calculate_target_for_specific_category")
    def test_check_objectives_compliance_passes_when_no_target(self, mock_calculate_target):
        """Should pass when target is None (no objective or already reached)."""
        mock_calculate_target.return_value = None

        mock_request = Mock()
        mock_request.entity.id = 1
        mock_request.GET = QueryDict("")

        data = {"type": Operation.TENEUR, "customs_category": "CONV", "biofuel": Mock(code="ETH")}
        selected_lots = []
        entity_id = 1
        declaration_year = 2025

        # Should not raise exception (no target = no check)
        OperationService.check_objectives_compliance(mock_request, selected_lots, data, entity_id, declaration_year)

    @patch("tiruert.services.operation.BalanceService.calculate_balance")
    @patch("tiruert.services.operation.ObjectiveService.calculate_target_for_specific_category")
    def test_check_services_method_are_called_with_data(
        self,
        mock_calculate_target,
        mock_calculate_balance,
    ):
        """Should call ObjectiveService and BalanceService with correct parameters (MJ unit)."""
        mock_calculate_target.return_value = 100000  # Dummy target
        mock_calculate_balance.return_value = {"balance_key": {"pending_teneur": 0, "declared_teneur": 0}}

        mock_request = Mock()
        mock_request.entity.id = 1
        mock_request.GET = QueryDict("")

        data = {"type": Operation.TENEUR, "customs_category": "CONV", "biofuel": Mock(code="ETH", pci_litre=21.3)}
        selected_lots = [{"id": 1, "volume": 1000}]
        entity_id = 1
        declaration_year = 2025

        # Call the method
        OperationService.check_objectives_compliance(mock_request, selected_lots, data, entity_id, declaration_year)

        # Verify ObjectiveService called with correct parameters
        mock_calculate_target.assert_called_once_with("CONV", 1)
        # Verify BalanceService called with correct parameters
        mock_calculate_balance.assert_called_once()
        called_args = mock_calculate_balance.call_args[0]
        self.assertEqual(called_args[1], 1)  # entity_id
        self.assertEqual(called_args[2], "customs_category")  # group_by
        self.assertEqual(called_args[3], "mj")  # unit
        self.assertEqual(mock_calculate_balance.call_args.kwargs["declaration_year"], declaration_year)

    @patch("tiruert.services.operation.BalanceService.calculate_balance")
    @patch("tiruert.services.operation.ObjectiveService.calculate_target_for_specific_category")
    def test_check_objectives_compliance_passes_when_below_target(
        self,
        mock_calculate_target,
        mock_calculate_balance,
    ):
        """Should pass when future teneur is below target."""
        # Target = 100,000 MJ
        mock_calculate_target.return_value = 100000

        # Current balance: 50,000 MJ pending + 20,000 MJ declared
        mock_calculate_balance.return_value = {"balance_key": {"pending_teneur": 50000, "declared_teneur": 20000}}

        mock_request = Mock()
        mock_request.entity.id = 1
        mock_request.GET = QueryDict("")

        data = {"type": Operation.TENEUR, "customs_category": "CONV", "biofuel": Mock(code="ETH", pci_litre=10)}

        # Request to add 1000L = 10,000 MJ
        # Future teneur: 50,000 + 20,000 + 10,000 = 80,000 MJ < 100,000 (OK)
        selected_lots = [{"id": 1, "volume": 1000}]
        entity_id = 1
        declaration_year = 2025

        # Should not raise exception
        OperationService.check_objectives_compliance(mock_request, selected_lots, data, entity_id, declaration_year)

    @patch("tiruert.services.operation.BalanceService.calculate_balance")
    @patch("tiruert.services.operation.ObjectiveService.calculate_target_for_specific_category")
    def test_check_objectives_compliance_raises_error_when_exceeds_target(
        self,
        mock_calculate_target,
        mock_calculate_balance,
    ):
        """Should raise ValidationError when future teneur exceeds target."""
        # Target = 100,000 MJ
        mock_calculate_target.return_value = 100000

        # Current balance: 80,000 MJ pending + 15,000 MJ declared
        mock_calculate_balance.return_value = {"balance_key": {"pending_teneur": 80000, "declared_teneur": 15000}}

        mock_request = Mock()
        mock_request.entity.id = 1
        mock_request.GET = QueryDict("")

        data = {"type": Operation.TENEUR, "customs_category": "CONV", "biofuel": Mock(code="ETH", pci_litre=10)}

        # Request to add 2000L = 20,000 MJ
        # Future teneur: 80,000 + 15,000 + 20,000 = 115,000 MJ > 100,000 (ERROR)
        selected_lots = [{"id": 1, "volume": 2000}]
        entity_id = 1
        declaration_year = 2025

        with self.assertRaises(ValidationError) as context:
            OperationService.check_objectives_compliance(mock_request, selected_lots, data, entity_id, declaration_year)

        self.assertIn("teneur", context.exception.detail.keys())
        error_message = str(context.exception.detail["teneur"])
        self.assertIn("20000", error_message)
        self.assertIn("100000", error_message)

    @patch("tiruert.services.operation.BalanceService.calculate_balance")
    @patch("tiruert.services.operation.ObjectiveService.calculate_target_for_specific_category")
    def test_check_objectives_compliance_applies_renewable_energy_share(
        self,
        mock_calculate_target,
        mock_calculate_balance,
    ):
        """Should include renewable_energy_share when converting selected lot volumes to MJ."""
        # With RES=0.5 and 1000L at PCI=10, teneur_to_add is 5000 MJ.
        # Without RES it would be 10000 MJ and this test would fail.
        mock_calculate_target.return_value = 7000
        mock_calculate_balance.return_value = {"balance_key": {"pending_teneur": 0, "declared_teneur": 0}}

        mock_request = Mock()
        mock_request.entity.id = 1
        mock_request.GET = QueryDict("")

        data = {
            "type": Operation.TENEUR,
            "customs_category": "CONV",
            "biofuel": Mock(code="ETH", pci_litre=10),
            "renewable_energy_share": 0.5,
        }

        selected_lots = [{"id": 1, "volume": 1000}]

        OperationService.check_objectives_compliance(mock_request, selected_lots, data, entity_id=1, declaration_year=2025)

        mock_calculate_target.assert_called_once_with("CONV", 1)

    @patch("tiruert.services.operation.BalanceService.calculate_balance")
    @patch("tiruert.services.operation.ObjectiveService.calculate_target_for_specific_category")
    def test_check_objectives_compliance_truncates_teneur_to_add_after_total_sum(
        self,
        mock_calculate_target,
        mock_calculate_balance,
    ):
        """Should truncate teneur_to_add at MJ level after summing all lots."""
        mock_calculate_target.return_value = 117
        mock_calculate_balance.return_value = {"balance_key": {"pending_teneur": 0, "declared_teneur": 0}}

        mock_request = Mock()
        mock_request.entity.id = 1
        mock_request.GET = QueryDict("")

        data = {"type": Operation.TENEUR, "customs_category": "CONV", "biofuel": Mock(code="ETH", pci_litre=27)}
        selected_lots = [
            {"id": 1, "volume": 2.19},
            {"id": 2, "volume": 2.19},
        ]  # results in 2.19*27 + 2.19*27 = 118.26 MJ, which exceeds target of 117 MJ

        with self.assertRaises(ValidationError) as context:
            OperationService.check_objectives_compliance(
                mock_request,
                selected_lots,
                data,
                entity_id=1,
                declaration_year=2025,
            )

        self.assertIn("teneur", context.exception.detail.keys())
        error_message = str(context.exception.detail["teneur"])
        self.assertIn("(118 MJ)", error_message)
        self.assertIn("(117 MJ)", error_message)

    def test_check_objectives_compliance_skips_for_non_teneur_operations(self):
        """Should skip check for non-TENEUR operation types."""
        mock_request = Mock()
        data = {"type": Operation.CESSION}  # Not TENEUR
        selected_lots = []
        entity_id = 1

        # Should not raise exception (early return for non-TENEUR)
        OperationService.check_objectives_compliance(
            mock_request,
            selected_lots,
            data,
            entity_id,
            declaration_year=None,
        )


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


class OperationServiceCalculateVolumeEthanol15Test(TestCase):
    """Tests for OperationService.calculate_volume_ethanol_15()."""

    def test_calculate_volume_ethanol_15_converts_eth_lot_volume(self):
        """Should mutate ETH lot volume in place with 0.995 factor and business truncation."""
        lot_eth = Mock()
        lot_eth.biofuel = Mock(code="ETH")
        lot_eth.volume = 1234.567

        result = OperationService.calculate_volume_ethanol_15([lot_eth])

        self.assertIsNone(result)
        self.assertEqual(lot_eth.volume, 1228.39)

    def test_calculate_volume_ethanol_15_keeps_non_eth_lot_unchanged(self):
        """Should keep non-ETH lots untouched."""
        lot_emag = Mock()
        lot_emag.biofuel = Mock(code="EMAG")
        lot_emag.volume = 750.0

        result = OperationService.calculate_volume_ethanol_15([lot_emag])

        self.assertIsNone(result)
        self.assertEqual(lot_emag.volume, 750.0)


class OperationServiceConvertEmagLotsTest(TestCase):
    """Tests for OperationService.convert_emag_lots()."""

    fixtures = ["json/biofuels.json"]

    def test_convert_emag_lots_converts_supported_biofuel_codes(self):
        """Should mutate supported biofuels to the EMAG fixture instance."""
        lots = [Mock(biofuel=Mock(code=code)) for code in ["EMHV", "EMHU", "EMHA", "B100"]]

        result = OperationService.convert_emag_lots(lots)

        emag = Biocarburant.objects.get(code="EMAG")
        self.assertIsNone(result)
        for lot in lots:
            self.assertEqual(lot.biofuel, emag)

    def test_convert_emag_lots_keeps_other_biofuels_unchanged(self):
        """Should leave non-supported biofuel objects untouched."""
        original_biofuel = Mock(code="ETH")
        lot = Mock(biofuel=original_biofuel)

        result = OperationService.convert_emag_lots([lot])

        self.assertIsNone(result)
        self.assertIs(lot.biofuel, original_biofuel)


class OperationServiceCreditedEntityFallbackTest(TestCase):
    """Test that credited_entity falls back to carbure_producer then carbure_supplier."""

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
        cls.operator = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        cls.trader = Entity.objects.filter(entity_type=Entity.TRADER).first()
        cls.depot = Depot.objects.first()
        cls.feedstock_conv = MatierePremiere.biofuel.filter(category="CONV").first()
        cls.biofuel_eth = Biocarburant.objects.get(code="ETH")

    def test_credited_entity_uses_carbure_supplier_when_no_client(self):
        """Should use carbure_supplier as credited_entity when carbure_client is None."""
        lot = CarbureLotFactory.create(
            carbure_client=None,
            carbure_supplier=self.trader,
            feedstock=self.feedstock_conv,
            biofuel=self.biofuel_eth,
            lot_status="ACCEPTED",
            delivery_type="RFC",
            volume=1000,
            ghg_total=5.0,
            carbure_delivery_site=self.depot,
        )

        lots_qs = CarbureLot.objects.filter(id=lot.id)
        OperationService.create_operations_from_lots(lots_qs)

        operation = Operation.objects.get(type=Operation.MAC_BIO)
        self.assertEqual(operation.credited_entity, self.trader)

    def test_credited_entity_prefers_carbure_client_over_supplier(self):
        """Should prefer carbure_client over carbure_supplier."""
        lot = CarbureLotFactory.create(
            carbure_client=self.operator,
            carbure_supplier=self.trader,
            feedstock=self.feedstock_conv,
            biofuel=self.biofuel_eth,
            lot_status="ACCEPTED",
            delivery_type="RFC",
            volume=1000,
            ghg_total=5.0,
            carbure_delivery_site=self.depot,
        )

        lots_qs = CarbureLot.objects.filter(id=lot.id)
        OperationService.create_operations_from_lots(lots_qs)

        operation = Operation.objects.get(type=Operation.MAC_BIO)
        self.assertEqual(operation.credited_entity, self.operator)


class OperationServiceBulkCheckVolumesTest(TestCase):
    """Tests for OperationService.bulk_check_volumes()."""

    @patch("tiruert.services.operation.OperationService.check_volumes")
    def test_bulk_check_volumes_groups_and_aggregates_duplicate_lots(self, mock_check_volumes):
        """Should aggregate volumes by (biofuel, customs_category) before checking."""
        biofuel_eth = Mock(id=1, code="ETH")
        biofuel_emag = Mock(id=2, code="EMAG")
        debited_entity = Mock(id=10)

        entries = [
            {
                "biofuel": biofuel_eth,
                "customs_category": "CONV",
                "debited_entity": debited_entity,
                "selected_lots": [{"id": 1, "volume": 700}],
            },
            {
                "biofuel": biofuel_eth,
                "customs_category": "CONV",
                "debited_entity": debited_entity,
                "selected_lots": [{"id": 1, "volume": 400}, {"id": 2, "volume": 100}],
            },
            {
                "biofuel": biofuel_emag,
                "customs_category": "ANN-IX-A",
                "debited_entity": debited_entity,
                "selected_lots": [{"id": 3, "volume": 50}],
            },
        ]

        OperationService.bulk_check_volumes(entries)

        self.assertEqual(mock_check_volumes.call_count, 2)

        observed = {}
        for call in mock_check_volumes.call_args_list:
            selected_lots, data = call.args
            observed[(data["biofuel"].code, data["customs_category"])] = {lot["id"]: lot["volume"] for lot in selected_lots}
            self.assertEqual(data["debited_entity"], debited_entity)

        self.assertEqual(observed[("ETH", "CONV")], {1: 1100, 2: 100})
        self.assertEqual(observed[("EMAG", "ANN-IX-A")], {3: 50})


class OperationServiceBulkCheckObjectivesComplianceTest(TestCase):
    """Tests for OperationService.bulk_check_objectives_compliance()."""

    @patch("tiruert.services.operation.OperationService._check_teneur_target")
    def test_bulk_check_objectives_compliance_aggregates_by_customs_category(self, mock_check_teneur_target):
        """Should sum teneur volumes per customs category before checking objectives."""
        request = Mock()
        request.entity.id = 1
        biofuel_eth = Mock(code="ETH", pci_litre=10)
        biofuel_emag = Mock(code="EMAG", pci_litre=20)

        entries = [
            {
                "customs_category": "CONV",
                "biofuel": biofuel_eth,
                "selected_lots": [{"id": 1, "volume": 100}],
            },
            {
                "customs_category": "CONV",
                "biofuel": biofuel_emag,
                "selected_lots": [{"id": 2, "volume": 50}],
            },
        ]

        declaration_year = 2025

        OperationService.bulk_check_objectives_compliance(request, 1, entries, declaration_year)

        mock_check_teneur_target.assert_called_once_with(request, 1, "CONV", 2000, declaration_year, bulk=True)

    @patch("tiruert.services.operation.OperationService._check_teneur_target")
    def test_bulk_check_objectives_compliance_applies_renewable_energy_share(self, mock_check_teneur_target):
        """Should include renewable_energy_share for each entry when aggregating MJ by category."""
        request = Mock()
        request.entity.id = 1
        biofuel_eth = Mock(code="ETH", pci_litre=10)

        entries = [
            {
                "customs_category": "CONV",
                "biofuel": biofuel_eth,
                "renewable_energy_share": 0.5,
                "selected_lots": [{"id": 1, "volume": 100}],
            },
            {
                "customs_category": "CONV",
                "biofuel": biofuel_eth,
                "renewable_energy_share": 1,
                "selected_lots": [{"id": 2, "volume": 50}],
            },
        ]

        OperationService.bulk_check_objectives_compliance(request, 1, entries, declaration_year=2025)

        # 100L * 10 * 0.5 + 50L * 10 * 1 = 1000 MJ
        mock_check_teneur_target.assert_called_once_with(request, 1, "CONV", 1000, 2025, bulk=True)


class OperationServiceDefineSectorTest(TestCase):
    """Tests for OperationService.define_sector()."""

    def test_define_sector_returns_essence_for_compatible_essence_biofuel(self):
        """Should return ESSENCE when the biofuel is essence-compatible."""
        biofuel = Mock(code="ETH", compatible_essence=True, compatible_diesel=False)

        result = OperationService.define_sector(biofuel)

        self.assertEqual(result, Operation.ESSENCE)

    def test_define_sector_returns_gazole_for_compatible_diesel_biofuel(self):
        """Should return GAZOLE when the biofuel is diesel-compatible."""
        biofuel = Mock(code="EMHV", compatible_essence=False, compatible_diesel=True)

        result = OperationService.define_sector(biofuel)

        self.assertEqual(result, Operation.GAZOLE)

    def test_define_sector_returns_gpl_for_compatible_gpl_biofuel(self):
        """Should return GPL_C when the biofuel is GPL-compatible."""
        biofuel = Mock(code="HCGPL", compatible_essence=False, compatible_diesel=False, compatible_gpl=True)

        result = OperationService.define_sector(biofuel)

        self.assertEqual(result, Operation.GPL_C)

    def test_define_sector_returns_carbureacteur_for_saf_biofuel(self):
        """Should return CARBUREACTEUR for SAF biofuel codes."""
        from saf.models.constants import SAF_BIOFUEL_TYPES

        biofuel = Mock(code=list(SAF_BIOFUEL_TYPES)[0], compatible_essence=False, compatible_diesel=False)

        result = OperationService.define_sector(biofuel)

        self.assertEqual(result, Operation.CARBUREACTEUR)

    def test_define_sector_returns_none_when_no_sector_matches(self):
        """Should return None when the biofuel matches no sector."""
        biofuel = Mock(code="UNKNOWN", compatible_essence=False, compatible_diesel=False, compatible_gpl=False)

        result = OperationService.define_sector(biofuel)

        self.assertIsNone(result)


class OperationServiceBuildDetailsDataTest(TestCase):
    """Tests for OperationService.build_details_data()."""

    def test_build_details_data_accepts_dict_like_input(self):
        """Should build detail payloads from a mapping of lot ids to volumes."""
        result = OperationService.build_details_data({1: 12.345, 2: 67.891}, {1: 0.5, 2: 1.25})

        self.assertEqual(
            result,
            [
                {"lot_id": 1, "volume": 12.34, "emission_rate_per_mj": 0.5},
                {"lot_id": 2, "volume": 67.89, "emission_rate_per_mj": 1.25},
            ],
        )

    def test_build_details_data_accepts_list_input(self):
        """Should build detail payloads from a list of lot dictionaries."""
        result = OperationService.build_details_data(
            [{"id": 3, "volume": 10.004}, {"id": 4, "volume": 20.006}],
            {3: 9.9, 4: 8.8},
        )

        self.assertEqual(
            result,
            [
                {"lot_id": 3, "volume": 10.0, "emission_rate_per_mj": 9.9},
                {"lot_id": 4, "volume": 20.00, "emission_rate_per_mj": 8.8},
            ],
        )
