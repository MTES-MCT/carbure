"""Tests for the common rule system used across biomethane services."""

from dataclasses import dataclass
from typing import Optional

from django.test import TestCase

from biomethane.services.rules import FieldClearingRule, RequiredFieldRule, RuleBuilder


@dataclass
class MockContext:
    """Mock context for testing rules."""

    value: Optional[str] = None
    items: Optional[list] = None
    contract: Optional[object] = None


@dataclass
class MockContract:
    """Mock contract for testing."""

    installation_category: str = "CATEGORY_1"


class FieldClearingRuleTests(TestCase):
    """Tests for FieldClearingRule dataclass."""

    def test_create_field_clearing_rule(self):
        """Test that a FieldClearingRule can be created with required fields."""
        rule = FieldClearingRule(
            name="test_rule",
            fields=["field1", "field2"],
            condition=lambda ctx: True,
        )

        self.assertEqual(rule.name, "test_rule")
        self.assertEqual(rule.fields, ["field1", "field2"])
        self.assertTrue(callable(rule.condition))

    def test_field_clearing_rule_condition_execution(self):
        """Test that the condition function can be executed."""
        rule = FieldClearingRule(
            name="test_rule",
            fields=["field1"],
            condition=lambda ctx: ctx.value == "expected",
        )

        context = MockContext(value="expected")
        self.assertTrue(rule.condition(context))

        context = MockContext(value="other")
        self.assertFalse(rule.condition(context))


class RequiredFieldRuleTests(TestCase):
    """Tests for RequiredFieldRule dataclass."""

    def test_create_required_field_rule(self):
        """Test that a RequiredFieldRule can be created with required fields."""
        rule = RequiredFieldRule(
            name="test_required_rule",
            fields=["field1", "field2"],
            condition=lambda ctx: True,
        )

        self.assertEqual(rule.name, "test_required_rule")
        self.assertEqual(rule.fields, ["field1", "field2"])
        self.assertTrue(callable(rule.condition))

    def test_required_field_rule_condition_execution(self):
        """Test that the condition function can be executed."""
        rule = RequiredFieldRule(
            name="test_required_rule",
            fields=["field1"],
            condition=lambda ctx: ctx.value == "required",
        )

        context = MockContext(value="required")
        self.assertTrue(rule.condition(context))

        context = MockContext(value="optional")
        self.assertFalse(rule.condition(context))


class RuleBuilderValueNotInListTests(TestCase):
    """Tests for RuleBuilder.value_not_in_list method."""

    def test_value_not_in_list_clears_when_value_not_allowed(self):
        """Test that fields are cleared when value is not in allowed list."""
        rule = RuleBuilder.value_not_in_list(
            get_value_from_context=lambda ctx: ctx.value,
            allowed_values=["A", "B", "C"],
            fields=["field1", "field2"],
            name="test_rule",
        )

        # Value not in allowed list - should clear
        context = MockContext(value="D")
        self.assertTrue(rule.condition(context))

    def test_value_not_in_list_keeps_when_value_allowed(self):
        """Test that fields are NOT cleared when value is in allowed list."""
        rule = RuleBuilder.value_not_in_list(
            get_value_from_context=lambda ctx: ctx.value,
            allowed_values=["A", "B", "C"],
            fields=["field1", "field2"],
            name="test_rule",
        )

        # Value in allowed list - should NOT clear
        context = MockContext(value="B")
        self.assertFalse(rule.condition(context))

    def test_value_not_in_list_with_none_value(self):
        """Test behavior when extracted value is None."""
        rule = RuleBuilder.value_not_in_list(
            get_value_from_context=lambda ctx: ctx.value,
            allowed_values=["A", "B"],
            fields=["field1"],
            name="test_rule",
        )

        # None is not in the allowed list - should clear
        context = MockContext(value=None)
        self.assertTrue(rule.condition(context))

    def test_value_not_in_list_with_numeric_values(self):
        """Test with numeric values."""
        rule = RuleBuilder.value_not_in_list(
            get_value_from_context=lambda ctx: ctx.value,
            allowed_values=[2011, 2020, 2021],
            fields=["field1"],
            name="test_rule",
        )

        context = MockContext(value=2023)
        self.assertTrue(rule.condition(context))

        context = MockContext(value=2020)
        self.assertFalse(rule.condition(context))


class RuleBuilderRequiredValueNotInListTests(TestCase):
    """Tests for RuleBuilder.required_value_not_in_list method."""

    def test_required_value_not_in_list_clears_when_value_absent(self):
        """Test that fields are cleared when required value is not in context list."""
        rule = RuleBuilder.required_value_not_in_list(
            get_list_from_context=lambda ctx: ctx.items,
            required_value="REQUIRED_ITEM",
            fields=["field1", "field2"],
            name="test_rule",
        )

        # Required value not in list - should clear
        context = MockContext(items=["OTHER_ITEM"])
        self.assertTrue(rule.condition(context))

    def test_required_value_not_in_list_keeps_when_value_present(self):
        """Test that fields are NOT cleared when required value is in context list."""
        rule = RuleBuilder.required_value_not_in_list(
            get_list_from_context=lambda ctx: ctx.items,
            required_value="REQUIRED_ITEM",
            fields=["field1", "field2"],
            name="test_rule",
        )

        # Required value in list - should NOT clear
        context = MockContext(items=["REQUIRED_ITEM", "OTHER_ITEM"])
        self.assertFalse(rule.condition(context))

    def test_required_value_not_in_list_with_empty_list(self):
        """Test behavior when context list is empty."""
        rule = RuleBuilder.required_value_not_in_list(
            get_list_from_context=lambda ctx: ctx.items,
            required_value="REQUIRED_ITEM",
            fields=["field1"],
            name="test_rule",
        )

        # Empty list - should clear
        context = MockContext(items=[])
        self.assertTrue(rule.condition(context))

    def test_required_value_not_in_list_with_none_list(self):
        """Test behavior when context list is None."""
        rule = RuleBuilder.required_value_not_in_list(
            get_list_from_context=lambda ctx: ctx.items,
            required_value="REQUIRED_ITEM",
            fields=["field1"],
            name="test_rule",
        )

        # None treated as empty list - should clear
        context = MockContext(items=None)
        self.assertTrue(rule.condition(context))


class RuleBuilderContractCategoryNotTests(TestCase):
    """Tests for RuleBuilder.contract_category_not method."""

    def test_contract_category_not_clears_when_category_differs(self):
        """Test that fields are cleared when contract category is different."""
        rule = RuleBuilder.contract_category_not(
            category="CATEGORY_2",
            fields=["field1", "field2"],
            name="test_rule",
        )

        # Contract has different category - should clear
        context = MockContext(contract=MockContract(installation_category="CATEGORY_1"))
        self.assertTrue(rule.condition(context))

    def test_contract_category_not_keeps_when_category_matches(self):
        """Test that fields are NOT cleared when contract category matches."""
        rule = RuleBuilder.contract_category_not(
            category="CATEGORY_2",
            fields=["field1", "field2"],
            name="test_rule",
        )

        # Contract has matching category - should NOT clear
        context = MockContext(contract=MockContract(installation_category="CATEGORY_2"))
        self.assertFalse(rule.condition(context))

    def test_contract_category_not_with_no_contract(self):
        """Test behavior when context has no contract."""
        rule = RuleBuilder.contract_category_not(
            category="CATEGORY_2",
            fields=["field1"],
            name="test_rule",
        )

        # No contract - should NOT clear (condition is False)
        context = MockContext(contract=None)
        self.assertFalse(rule.condition(context))


class RuleBuilderIntegrationTests(TestCase):
    """Integration tests for multiple rules working together."""

    def test_multiple_rules_evaluation(self):
        """Test that multiple rules can be evaluated together."""
        rules = [
            RuleBuilder.value_not_in_list(
                lambda ctx: ctx.value,
                ["A", "B"],
                ["field1"],
                "value_rule",
            ),
            RuleBuilder.required_value_not_in_list(
                lambda ctx: ctx.items,
                "REQUIRED",
                ["field2"],
                "list_rule",
            ),
        ]

        # Both rules should clear
        context = MockContext(value="C", items=["OTHER"])
        fields_to_clear = []
        for rule in rules:
            if rule.condition(context):
                fields_to_clear.extend(rule.fields)

        self.assertEqual(sorted(fields_to_clear), ["field1", "field2"])

    def test_rule_fields_can_overlap(self):
        """Test that multiple rules can target the same fields."""
        rules = [
            RuleBuilder.value_not_in_list(
                lambda ctx: ctx.value,
                ["A"],
                ["field1", "field2"],
                "rule1",
            ),
            RuleBuilder.required_value_not_in_list(
                lambda ctx: ctx.items,
                "REQUIRED",
                ["field2", "field3"],
                "rule2",
            ),
        ]

        context = MockContext(value="B", items=[])
        fields_to_clear = []
        for rule in rules:
            if rule.condition(context):
                fields_to_clear.extend(rule.fields)

        # field2 appears twice but should be deduplicated by caller
        self.assertIn("field1", fields_to_clear)
        self.assertIn("field2", fields_to_clear)
        self.assertIn("field3", fields_to_clear)
