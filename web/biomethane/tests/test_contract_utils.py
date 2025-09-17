from django.test import TestCase

from biomethane.models.biomethane_contract import BiomethaneContract
from biomethane.models.biomethane_contract_amendment import BiomethaneContractAmendment
from biomethane.utils.contract import get_tracked_amendment_types
from core.models import Entity


class ContractUtilsTests(TestCase):
    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    def test_tracked_amendment_types_handler_appends_contract_changed(self):
        """Test that tracked_amendment_types is updated with existing types and new values."""
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

        current_tracked_types = get_tracked_amendment_types(
            contract, {"cmax": 150.0, "cmax_annualized": True, "buyer": new_buyer}
        )

        self.assertEqual(
            current_tracked_types,
            [
                BiomethaneContractAmendment.INPUT_BONUS_UPDATE,
                BiomethaneContractAmendment.CMAX_ANNUALIZATION,
                BiomethaneContractAmendment.CMAX_PAP_UPDATE,
                BiomethaneContractAmendment.PRODUCER_BUYER_INFO_CHANGE,
            ],
        )

    def test_tracked_amendment_types_handler_add_value_to_none_list(self):
        """Test that tracked_amendment_types is updated with CMAX_PAP_UPDATE."""
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
        )

        current_tracked_types = get_tracked_amendment_types(contract, {"cmax": 150.0})

        self.assertEqual(
            current_tracked_types,
            [BiomethaneContractAmendment.CMAX_PAP_UPDATE],
        )

    def test_tracked_amendment_types_handler_returns_same_list_if_no_change(self):
        """Test that tracked_amendment_types is returned unchanged if same tracked_amendment_types are provided."""
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            tracked_amendment_types=[BiomethaneContractAmendment.CMAX_PAP_UPDATE],
        )

        current_tracked_types = get_tracked_amendment_types(contract, {"cmax": 150.0})

        self.assertEqual(
            current_tracked_types,
            [BiomethaneContractAmendment.CMAX_PAP_UPDATE],
        )
