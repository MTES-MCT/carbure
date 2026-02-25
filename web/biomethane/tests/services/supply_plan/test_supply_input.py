"""Unit tests for supply_plan.supply_input business rules service."""

from django.test import TestCase

from biomethane.models import BiomethaneSupplyInput
from biomethane.services.supply_plan.supply_input import (
    apply_input_name_field_rules,
)
from core.models import MatierePremiere
from feedstocks.models import Classification


class ApplyInputNameFieldRulesTests(TestCase):
    """Tests for apply_input_name_field_rules()."""

    def setUp(self):
        self.input_mais = MatierePremiere.objects.create(
            name="Maïs",
            name_en="Corn",
            code="MAIS",
            is_methanogenic=True,
        )
        classification_cive = Classification.objects.create(
            group="Biomasse",
            category="Biomasse agricole - Cultures intermédiaires",
            subcategory="CIVE",
        )
        self.input_seigle_cive = MatierePremiere.objects.create(
            name="Seigle - CIVE",
            name_en="Rye - CIVE",
            code="SEIGLE_CIVE",
            is_methanogenic=True,
            classification=classification_cive,
        )
        self.input_autres_cultures = MatierePremiere.objects.create(
            name="Autres cultures",
            name_en="Other crops",
            code="AUTRES_CULTURES",
            is_methanogenic=True,
        )
        self.input_huiles_animale = MatierePremiere.objects.create(
            name="Huiles alimentaires usagées d'origine animale",
            name_en="Used cooking oil animal",
            code="HUILES_ANIMALE",
            is_methanogenic=True,
        )
        # Input matching both CIVE and culture_details (AUTRES_CULTURES_CIVE)
        self.input_autres_cive = MatierePremiere.objects.create(
            name="Autres cultures CIVE",
            name_en="Other crops CIVE",
            code="AUTRES_CULTURES_CIVE",
            is_methanogenic=True,
            classification=classification_cive,
        )

    def test_no_input_name_clears_all_conditional_fields(self):
        """When input_name is None, all rule fields are set to None."""
        data = {
            "input_name": None,
            "type_cive": BiomethaneSupplyInput.SUMMER,
            "culture_details": "Some",
            "collection_type": BiomethaneSupplyInput.PRIVATE,
        }
        errors = apply_input_name_field_rules(data)
        self.assertEqual(errors, {})
        self.assertIsNone(data["type_cive"])
        self.assertIsNone(data["culture_details"])
        self.assertIsNone(data["collection_type"])

    def test_no_input_name_returns_no_errors(self):
        """When input_name is None, returned errors dict is empty."""
        data = {"input_name": None}
        errors = apply_input_name_field_rules(data)
        self.assertEqual(errors, {})

    def test_type_cive_required_when_classification_category_matches(self):
        """When input has CIVE classification category, type_cive is required."""
        data = {
            "input_name": self.input_seigle_cive,
            "type_cive": None,
            "culture_details": None,
            "collection_type": None,
        }
        errors = apply_input_name_field_rules(data)
        self.assertEqual(errors, {"type_cive": "Le type de CIVE est requis pour cet intrant."})
        self.assertIsNone(data["culture_details"])
        self.assertIsNone(data["collection_type"])

    def test_type_cive_valid_when_classification_category_matches(self):
        """When input has CIVE category and type_cive is set, no error."""
        data = {
            "input_name": self.input_seigle_cive,
            "type_cive": BiomethaneSupplyInput.WINTER,
            "culture_details": None,
            "collection_type": None,
        }
        errors = apply_input_name_field_rules(data)
        self.assertEqual(errors, {})
        self.assertEqual(data["type_cive"], BiomethaneSupplyInput.WINTER)

    def test_type_cive_cleared_when_classification_does_not_match(self):
        """When input has no CIVE category, type_cive is cleared to None."""
        data = {
            "input_name": self.input_mais,
            "type_cive": BiomethaneSupplyInput.SUMMER,
            "culture_details": None,
            "collection_type": None,
        }
        errors = apply_input_name_field_rules(data)
        self.assertEqual(errors, {})
        self.assertIsNone(data["type_cive"])

    def test_type_cive_cleared_when_classification_is_none(self):
        """When input has no classification, type_cive rule does not match."""
        data = {
            "input_name": self.input_mais,
            "type_cive": BiomethaneSupplyInput.SUMMER,
            "culture_details": None,
            "collection_type": None,
        }
        errors = apply_input_name_field_rules(data)
        self.assertEqual(errors, {})
        self.assertIsNone(data["type_cive"])

    def test_culture_details_required_when_code_in_rule(self):
        """When input code is AUTRES_CULTURES, culture_details is required."""
        data = {
            "input_name": self.input_autres_cultures,
            "type_cive": None,
            "culture_details": None,
            "collection_type": None,
        }
        errors = apply_input_name_field_rules(data)
        self.assertEqual(
            errors,
            {"culture_details": "Précisez la culture pour cet intrant."},
        )

    def test_culture_details_valid_when_code_in_rule(self):
        """When input code matches and culture_details is set, no error."""
        data = {
            "input_name": self.input_autres_cultures,
            "type_cive": None,
            "culture_details": "Mélange céréales",
            "collection_type": None,
        }
        errors = apply_input_name_field_rules(data)
        self.assertEqual(errors, {})
        self.assertEqual(data["culture_details"], "Mélange céréales")

    def test_culture_details_cleared_when_code_not_in_rule(self):
        """When input code is not in rule, culture_details is cleared."""
        data = {
            "input_name": self.input_mais,
            "type_cive": None,
            "culture_details": "Some",
            "collection_type": None,
        }
        errors = apply_input_name_field_rules(data)
        self.assertEqual(errors, {})
        self.assertIsNone(data["culture_details"])

    def test_collection_type_required_when_name_in_rule(self):
        """When input name is in collection_type list, field is required."""
        data = {
            "input_name": self.input_huiles_animale,
            "type_cive": None,
            "culture_details": None,
            "collection_type": None,
        }
        errors = apply_input_name_field_rules(data)
        self.assertEqual(
            errors,
            {"collection_type": "Le type de collecte est requis pour cet intrant."},
        )

    def test_collection_type_valid_when_name_in_rule(self):
        """When input name matches and collection_type is set, no error."""
        data = {
            "input_name": self.input_huiles_animale,
            "type_cive": None,
            "culture_details": None,
            "collection_type": BiomethaneSupplyInput.LOCAL,
        }
        errors = apply_input_name_field_rules(data)
        self.assertEqual(errors, {})
        self.assertEqual(data["collection_type"], BiomethaneSupplyInput.LOCAL)

    def test_collection_type_cleared_when_name_not_in_rule(self):
        """When input name is not in list, collection_type is cleared."""
        data = {
            "input_name": self.input_mais,
            "type_cive": None,
            "culture_details": None,
            "collection_type": BiomethaneSupplyInput.PRIVATE,
        }
        errors = apply_input_name_field_rules(data)
        self.assertEqual(errors, {})
        self.assertIsNone(data["collection_type"])

    def test_input_matching_no_rule_clears_all_conditional_fields(self):
        """When input matches no rule (e.g. Maïs), all conditional fields are cleared."""
        data = {
            "input_name": self.input_mais,
            "type_cive": BiomethaneSupplyInput.SUMMER,
            "culture_details": "Detail",
            "collection_type": BiomethaneSupplyInput.BOTH,
        }
        errors = apply_input_name_field_rules(data)
        self.assertEqual(errors, {})
        self.assertIsNone(data["type_cive"])
        self.assertIsNone(data["culture_details"])
        self.assertIsNone(data["collection_type"])

    def test_multiple_rules_match_returns_multiple_errors(self):
        """When input matches several rules and fields are empty, all errors are returned."""
        data = {
            "input_name": self.input_autres_cive,
            "type_cive": None,
            "culture_details": None,
            "collection_type": None,
        }
        errors = apply_input_name_field_rules(data)
        self.assertIn("type_cive", errors)
        self.assertIn("culture_details", errors)
        self.assertEqual(len(errors), 2)
