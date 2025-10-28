from django.test import TestCase

from biomethane.models.biomethane_contract import BiomethaneContract
from biomethane.models.biomethane_contract_amendment import BiomethaneContractAmendment
from biomethane.services.contract import BiomethaneContractService
from core.models import Entity


class BiomethaneContractServiceTests(TestCase):
    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    def test_handle_is_red_ii_disables_when_cmax_below_threshold(self):
        """Test that handle_is_red_ii disables Red II when cmax <= 200 and user wants to disable."""
        # Setup producer with Red II enabled
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        validated_data = {
            "cmax": 150.0,  # Below threshold
            "is_red_ii": False,  # User wants to disable
        }

        BiomethaneContractService.handle_is_red_ii(validated_data, self.producer_entity)

        self.producer_entity.refresh_from_db()
        self.assertFalse(self.producer_entity.is_red_ii)
        self.assertNotIn("is_red_ii", validated_data)

    def test_handle_is_red_ii_disables_when_pap_below_threshold(self):
        """Test that handle_is_red_ii disables Red II when pap_contracted <= 19.5."""
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        validated_data = {
            "pap_contracted": 15.0,  # Below threshold
            "is_red_ii": False,
        }

        BiomethaneContractService.handle_is_red_ii(validated_data, self.producer_entity)

        self.producer_entity.refresh_from_db()
        self.assertFalse(self.producer_entity.is_red_ii)

    def test_handle_is_red_ii_no_change_when_above_threshold(self):
        """Test that handle_is_red_ii doesn't change Red II when values are above threshold."""
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        validated_data = {
            "cmax": 250.0,  # Above threshold
            "is_red_ii": False,  # User wants to disable but can't
        }

        BiomethaneContractService.handle_is_red_ii(validated_data, self.producer_entity)

        self.producer_entity.refresh_from_db()
        self.assertTrue(self.producer_entity.is_red_ii)  # Should remain True

    def test_handle_is_red_ii_no_change_when_is_red_ii_not_false(self):
        """Test that handle_is_red_ii only acts when is_red_ii is explicitly False."""
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        validated_data = {
            "cmax": 150.0,  # Below threshold
            "is_red_ii": True,  # User doesn't want to disable
        }

        BiomethaneContractService.handle_is_red_ii(validated_data, self.producer_entity)

        self.producer_entity.refresh_from_db()
        self.assertTrue(self.producer_entity.is_red_ii)  # Should remain True

    def test_get_tracked_amendment_types_appends_multiple_types(self):
        """Test that tracked_amendment_types is updated with existing types and new values, sorted alphabetically."""
        buyer_entity = Entity.objects.create(
            name="Buyer",
            entity_type=Entity.OPERATOR,
        )
        new_buyer = Entity.objects.create(
            name="New Buyer",
            entity_type=Entity.OPERATOR,
        )
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            buyer=buyer_entity,
            cmax=100.0,
            tracked_amendment_types=[BiomethaneContractAmendment.INPUT_BONUS_UPDATE],
        )

        current_tracked_types = BiomethaneContractService.get_tracked_amendment_types(
            contract, {"cmax": 150.0, "cmax_annualized": True, "buyer": new_buyer}
        )

        self.assertEqual(
            current_tracked_types,
            [
                BiomethaneContractAmendment.CMAX_ANNUALIZATION,
                BiomethaneContractAmendment.CMAX_PAP_UPDATE,
                BiomethaneContractAmendment.INPUT_BONUS_UPDATE,
                BiomethaneContractAmendment.PRODUCER_BUYER_INFO_CHANGE,
            ],
        )

    def test_get_tracked_amendment_types_add_value_to_none_list(self):
        """Test that tracked_amendment_types is updated with CMAX_PAP_UPDATE."""
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
        )

        current_tracked_types = BiomethaneContractService.get_tracked_amendment_types(contract, {"cmax": 150.0})

        self.assertEqual(
            current_tracked_types,
            [BiomethaneContractAmendment.CMAX_PAP_UPDATE],
        )

    def test_get_tracked_amendment_types_returns_same_list_if_no_change(self):
        """Test that tracked_amendment_types is returned unchanged if same tracked_amendment_types are provided."""
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            tracked_amendment_types=[BiomethaneContractAmendment.CMAX_PAP_UPDATE],
        )

        current_tracked_types = BiomethaneContractService.get_tracked_amendment_types(contract, {"cmax": 150.0})

        self.assertEqual(
            current_tracked_types,
            [BiomethaneContractAmendment.CMAX_PAP_UPDATE],
        )
