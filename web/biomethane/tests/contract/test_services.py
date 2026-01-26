from unittest.mock import Mock

from django.test import TestCase

from biomethane.models.biomethane_contract import BiomethaneContract
from biomethane.models.biomethane_contract_amendment import BiomethaneContractAmendment
from biomethane.services.contract import (
    BiomethaneContractService,
    ContractValidationContext,
    _build_contract_clearing_rules,
    _build_required_field_rules,
)
from core.models import Entity


class ContractRulesConfigurationTests(TestCase):
    """Test the _build_contract_clearing_rules function configuration."""

    def setUp(self):
        self.rules = _build_contract_clearing_rules()

    def test_all_expected_rules_are_configured(self):
        """Test that all expected rule names are present in the configuration."""
        expected_rule_names = [
            "tariff_rule_1_clear_pap",
            "tariff_rule_2_clear_cmax",
            "cmax_not_annualized",
        ]

        actual_rule_names = [rule.name for rule in self.rules]
        self.assertEqual(expected_rule_names, actual_rule_names)

    def test_tariff_rule_1_clear_pap_fields_and_condition(self):
        """Test tariff_rule_1_clear_pap has correct fields and condition logic."""
        rule = next(r for r in self.rules if r.name == "tariff_rule_1_clear_pap")
        self.assertEqual(rule.fields, ["pap_contracted"])

        # Should trigger when tariff is in TARIFF_RULE_1 (2011, 2020)
        mock_contract = Mock()
        mock_contract.tariff_reference = "2011"
        self.assertTrue(rule.condition(mock_contract))

        mock_contract.tariff_reference = "2020"
        self.assertTrue(rule.condition(mock_contract))

        # Should not trigger when tariff is in TARIFF_RULE_2
        mock_contract.tariff_reference = "2021"
        self.assertFalse(rule.condition(mock_contract))

        mock_contract.tariff_reference = "2023"
        self.assertFalse(rule.condition(mock_contract))

    def test_tariff_rule_2_clear_cmax_fields_and_condition(self):
        """Test tariff_rule_2_clear_cmax has correct fields and condition logic."""
        rule = next(r for r in self.rules if r.name == "tariff_rule_2_clear_cmax")
        self.assertEqual(rule.fields, ["cmax", "cmax_annualized", "cmax_annualized_value"])

        # Should trigger when tariff is in TARIFF_RULE_2 (2021, 2023)
        mock_contract = Mock()
        mock_contract.tariff_reference = "2021"
        self.assertTrue(rule.condition(mock_contract))

        mock_contract.tariff_reference = "2023"
        self.assertTrue(rule.condition(mock_contract))

        # Should not trigger when tariff is in TARIFF_RULE_1
        mock_contract.tariff_reference = "2011"
        self.assertFalse(rule.condition(mock_contract))

        mock_contract.tariff_reference = "2020"
        self.assertFalse(rule.condition(mock_contract))

    def test_cmax_not_annualized_fields_and_condition(self):
        """Test cmax_not_annualized has correct fields and condition logic."""
        rule = next(r for r in self.rules if r.name == "cmax_not_annualized")
        self.assertEqual(rule.fields, ["cmax_annualized_value"])

        # Should trigger when cmax_annualized is explicitly False
        mock_contract = Mock()
        mock_contract.cmax_annualized = False
        self.assertTrue(rule.condition(mock_contract))

        # Should not trigger when cmax_annualized is True
        mock_contract.cmax_annualized = True
        self.assertFalse(rule.condition(mock_contract))

        # Should not trigger when cmax_annualized is None
        mock_contract.cmax_annualized = None
        self.assertFalse(rule.condition(mock_contract))


class ContractValidationContextTests(TestCase):
    """Test the ContractValidationContext dataclass and factory method."""

    def test_context_creation_with_all_fields(self):
        """Test that context can be created with all fields."""
        context = ContractValidationContext(
            is_creation=True,
            tariff_reference="2011",
            cmax_annualized=True,
            has_contract_document=False,
        )

        self.assertTrue(context.is_creation)
        self.assertEqual(context.tariff_reference, "2011")
        self.assertTrue(context.cmax_annualized)
        self.assertFalse(context.has_contract_document)

    def test_factory_method_for_creation(self):
        """Test factory method when creating a new contract (contract=None)."""
        validated_data = {
            "tariff_reference": "2021",
            "cmax_annualized": False,
        }

        context = ContractValidationContext.from_contract_and_data(None, validated_data)

        self.assertTrue(context.is_creation)
        self.assertEqual(context.tariff_reference, "2021")
        self.assertFalse(context.cmax_annualized)
        self.assertFalse(context.has_contract_document)

    def test_factory_method_for_update(self):
        """Test factory method when updating existing contract."""
        mock_contract = Mock()
        validated_data = {
            "tariff_reference": "2023",
            "cmax_annualized": None,
        }

        context = ContractValidationContext.from_contract_and_data(mock_contract, validated_data)

        self.assertFalse(context.is_creation)
        self.assertEqual(context.tariff_reference, "2023")
        self.assertIsNone(context.cmax_annualized)
        self.assertFalse(context.has_contract_document)

    def test_factory_method_detects_contract_document_fields(self):
        """Test that has_contract_document is True when any document field is present."""
        validated_data_with_signature = {
            "signature_date": "2022-01-15",
        }

        context = ContractValidationContext.from_contract_and_data(None, validated_data_with_signature)
        self.assertTrue(context.has_contract_document)

        validated_data_with_file = {
            "general_conditions_file": "some_file.pdf",
        }

        context = ContractValidationContext.from_contract_and_data(None, validated_data_with_file)
        self.assertTrue(context.has_contract_document)

    def test_factory_method_without_contract_document_fields(self):
        """Test that has_contract_document is False when no document fields present."""
        validated_data = {
            "tariff_reference": "2011",
            "cmax": 150.0,
        }

        context = ContractValidationContext.from_contract_and_data(None, validated_data)
        self.assertFalse(context.has_contract_document)


class RequiredFieldRulesConfigurationTests(TestCase):
    """Test the _build_required_field_rules function configuration."""

    def setUp(self):
        self.rules = _build_required_field_rules()

    def test_all_expected_rules_are_configured(self):
        """Test that all expected rule names are present in the configuration."""
        expected_rule_names = [
            "tariff_reference_on_creation",
            "tariff_rule_1_required",
            "tariff_rule_2_required",
            "cmax_annualized_requires_value",
            "contract_document_all_or_nothing",
        ]

        actual_rule_names = [rule.name for rule in self.rules]
        self.assertEqual(expected_rule_names, actual_rule_names)

    def test_tariff_reference_on_creation_fields_and_condition(self):
        """Test tariff_reference_on_creation has correct fields and condition logic."""
        rule = next(r for r in self.rules if r.name == "tariff_reference_on_creation")
        self.assertEqual(rule.fields, ["tariff_reference"])

        # Should require tariff_reference when creating (is_creation=True)
        context = ContractValidationContext(
            is_creation=True, tariff_reference=None, cmax_annualized=None, has_contract_document=False
        )
        self.assertTrue(rule.condition(context))

        # Should not require when updating (is_creation=False)
        context = ContractValidationContext(
            is_creation=False, tariff_reference=None, cmax_annualized=None, has_contract_document=False
        )
        self.assertFalse(rule.condition(context))

    def test_tariff_rule_1_required_fields_and_condition(self):
        """Test tariff_rule_1_required has correct fields and condition logic."""
        rule = next(r for r in self.rules if r.name == "tariff_rule_1_required")
        self.assertEqual(rule.fields, BiomethaneContractService.TARIFF_RULE_1_FIELDS)

        # Should require fields when tariff is in TARIFF_RULE_1 (2011, 2020)
        for tariff in ["2011", "2020"]:
            context = ContractValidationContext(
                is_creation=True, tariff_reference=tariff, cmax_annualized=None, has_contract_document=False
            )
            self.assertTrue(rule.condition(context), f"Should require fields for tariff {tariff}")

        # Should not require when tariff is in TARIFF_RULE_2
        for tariff in ["2021", "2023"]:
            context = ContractValidationContext(
                is_creation=True, tariff_reference=tariff, cmax_annualized=None, has_contract_document=False
            )
            self.assertFalse(rule.condition(context), f"Should not require fields for tariff {tariff}")

    def test_tariff_rule_2_required_fields_and_condition(self):
        """Test tariff_rule_2_required has correct fields and condition logic."""
        rule = next(r for r in self.rules if r.name == "tariff_rule_2_required")
        self.assertEqual(rule.fields, BiomethaneContractService.TARIFF_RULE_2_FIELDS)

        # Should require fields when tariff is in TARIFF_RULE_2 (2021, 2023)
        for tariff in ["2021", "2023"]:
            context = ContractValidationContext(
                is_creation=True, tariff_reference=tariff, cmax_annualized=None, has_contract_document=False
            )
            self.assertTrue(rule.condition(context), f"Should require fields for tariff {tariff}")

        # Should not require when tariff is in TARIFF_RULE_1
        for tariff in ["2011", "2020"]:
            context = ContractValidationContext(
                is_creation=True, tariff_reference=tariff, cmax_annualized=None, has_contract_document=False
            )
            self.assertFalse(rule.condition(context), f"Should not require fields for tariff {tariff}")

    def test_cmax_annualized_requires_value_fields_and_condition(self):
        """Test cmax_annualized_requires_value has correct fields and condition logic."""
        rule = next(r for r in self.rules if r.name == "cmax_annualized_requires_value")
        self.assertEqual(rule.fields, ["cmax_annualized_value"])

        # Should require cmax_annualized_value when cmax_annualized is True
        context = ContractValidationContext(
            is_creation=True, tariff_reference="2011", cmax_annualized=True, has_contract_document=False
        )
        self.assertTrue(rule.condition(context))

        # Should not require when cmax_annualized is False
        context = ContractValidationContext(
            is_creation=True, tariff_reference="2011", cmax_annualized=False, has_contract_document=False
        )
        self.assertFalse(rule.condition(context))

        # Should not require when cmax_annualized is None
        context = ContractValidationContext(
            is_creation=True, tariff_reference="2011", cmax_annualized=None, has_contract_document=False
        )
        self.assertFalse(rule.condition(context))

    def test_contract_document_all_or_nothing_fields_and_condition(self):
        """Test contract_document_all_or_nothing has correct fields and condition logic."""
        rule = next(r for r in self.rules if r.name == "contract_document_all_or_nothing")
        self.assertEqual(rule.fields, BiomethaneContractService.CONTRACT_DOCUMENT_FIELDS)

        # Should require all document fields when has_contract_document is True
        context = ContractValidationContext(
            is_creation=True, tariff_reference="2011", cmax_annualized=None, has_contract_document=True
        )
        self.assertTrue(rule.condition(context))

        # Should not require when has_contract_document is False
        context = ContractValidationContext(
            is_creation=True, tariff_reference="2011", cmax_annualized=None, has_contract_document=False
        )
        self.assertFalse(rule.condition(context))


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

    def test_validate_contract_creation_requires_tariff_reference(self):
        """Test that validate_contract requires tariff_reference for new contracts."""
        validated_data = {
            "cmax": 150.0,
            "buyer": self.producer_entity,
        }

        errors, required_fields = BiomethaneContractService.validate_contract(None, validated_data)

        self.assertIn("tariff_reference", required_fields)
        self.assertIsInstance(required_fields, list)

    def test_validate_contract_with_rule_1_tariff(self):
        """Test that validate_contract returns correct required fields for TARIFF_RULE_1."""
        validated_data = {
            "tariff_reference": "2011",  # TARIFF_RULE_1
            "cmax": 150.0,
        }

        errors, required_fields = BiomethaneContractService.validate_contract(None, validated_data)

        # Should require TARIFF_RULE_1 fields
        self.assertIn("cmax", required_fields)
        self.assertIn("cmax_annualized", required_fields)
        self.assertIn("installation_category", required_fields)
        self.assertIn("buyer", required_fields)

        # Should not require TARIFF_RULE_2 fields
        self.assertNotIn("pap_contracted", required_fields)

    def test_validate_contract_with_rule_2_tariff(self):
        """Test that validate_contract returns correct required fields for TARIFF_RULE_2."""
        validated_data = {
            "tariff_reference": "2021",  # TARIFF_RULE_2
            "pap_contracted": 25.0,
        }

        errors, required_fields = BiomethaneContractService.validate_contract(None, validated_data)

        # Should require TARIFF_RULE_2 fields
        self.assertIn("pap_contracted", required_fields)
        self.assertIn("installation_category", required_fields)
        self.assertIn("buyer", required_fields)

        # Should not require TARIFF_RULE_1 fields
        self.assertNotIn("cmax", required_fields)
        self.assertNotIn("cmax_annualized", required_fields)

    def test_clear_fields_based_on_tariff_rule_1(self):
        """Test that clear_fields_based_on_tariff clears pap_contracted for TARIFF_RULE_1."""
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            tariff_reference="2011",  # TARIFF_RULE_1
            cmax=150.0,
            pap_contracted=25.0,  # Should be cleared
        )

        update_data = BiomethaneContractService.clear_fields_based_on_tariff(contract)

        self.assertIn("pap_contracted", update_data)
        self.assertIsNone(update_data["pap_contracted"])

    def test_clear_fields_based_on_tariff_rule_2(self):
        """Test that clear_fields_based_on_tariff clears cmax fields for TARIFF_RULE_2."""
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            tariff_reference="2021",  # TARIFF_RULE_2
            pap_contracted=25.0,
            cmax=150.0,  # Should be cleared
            cmax_annualized=True,  # Should be cleared
        )

        update_data = BiomethaneContractService.clear_fields_based_on_tariff(contract)

        self.assertIn("cmax", update_data)
        self.assertIn("cmax_annualized", update_data)
        self.assertIn("cmax_annualized_value", update_data)
        self.assertIsNone(update_data["cmax"])
        self.assertFalse(update_data["cmax_annualized"])

    def test_clear_fields_based_on_tariff_clears_annualized_value_when_false(self):
        """Test that clear_fields_based_on_tariff clears cmax_annualized_value when cmax_annualized is False."""
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            tariff_reference="2011",  # TARIFF_RULE_1
            cmax=150.0,
            cmax_annualized=False,
            cmax_annualized_value=100.0,  # Should be cleared
        )

        update_data = BiomethaneContractService.clear_fields_based_on_tariff(contract)

        self.assertIn("cmax_annualized_value", update_data)
        self.assertIsNone(update_data["cmax_annualized_value"])
