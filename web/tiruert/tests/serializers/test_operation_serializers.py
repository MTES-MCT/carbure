from unittest.mock import Mock

from django.test import TestCase

from tiruert.models import Operation
from tiruert.serializers import OperationSerializer
from tiruert.serializers.operation import BaseOperationSerializer


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
                instance.quantity.assert_called_once_with(unit="mj")
                self.assertEqual(result, 72000.0)
