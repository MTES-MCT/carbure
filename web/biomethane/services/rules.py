"""
Common rule system for biomethane services.
Provides declarative field clearing rules and required field rules based on business logic conditions.
"""

from dataclasses import dataclass
from typing import Callable, TypeVar

# Generic context type for type hints
ContextType = TypeVar("ContextType")


@dataclass
class FieldClearingRule:
    """Rule to determine if fields should be cleared based on a condition."""

    name: str
    fields: list[str]
    condition: Callable[[ContextType], bool]


@dataclass
class RequiredFieldRule:
    """Rule to determine if fields should be required based on a condition."""

    name: str
    fields: list[str]
    condition: Callable[[ContextType], bool]


class RuleBuilder:
    """Factory to build common field clearing rules."""

    @staticmethod
    def value_not_in_list(
        get_value_from_context: Callable[[ContextType], any],
        allowed_values: list,
        fields: list[str],
        name: str,
    ) -> FieldClearingRule:
        """
        Create a rule that clears fields when a context value is NOT in a list of allowed values.

        Args:
            get_value_from_context: Function to extract the value from context
            allowed_values: List of allowed values (fields cleared if value not in this list)
            fields: Fields to clear if value not in allowed_values
            name: Rule identifier

        Returns:
            FieldClearingRule instance
        """

        def condition(ctx: ContextType) -> bool:
            value = get_value_from_context(ctx)
            return value not in allowed_values

        return FieldClearingRule(name, fields, condition)

    @staticmethod
    def required_value_not_in_list(
        get_list_from_context: Callable[[ContextType], list],
        required_value: any,
        fields: list[str],
        name: str,
    ) -> FieldClearingRule:
        """
        Create a rule that clears fields when a required value is NOT in a context list.

        Args:
            get_list_from_context: Function to extract the list from context
            required_value: Value that must be present in the list
            fields: Fields to clear if required_value is absent from the list
            name: Rule identifier

        Returns:
            FieldClearingRule instance
        """

        def condition(ctx: ContextType) -> bool:
            items = get_list_from_context(ctx) or []
            return required_value not in items

        return FieldClearingRule(name, fields, condition)

    @staticmethod
    def contract_category_not(category: str, fields: list[str], name: str) -> FieldClearingRule:
        """
        Create a rule that clears fields when contract category differs.

        Args:
            category: Expected contract category
            fields: Fields to clear if category differs
            name: Rule identifier

        Returns:
            FieldClearingRule instance
        """

        def condition(ctx: ContextType) -> bool:
            return ctx.contract and ctx.contract.installation_category != category

        return FieldClearingRule(name, fields, condition)
