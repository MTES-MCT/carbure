from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework import serializers

from core.models import Entity
from tiruert.models.elec_operation import ElecOperation
from tiruert.serializers import (
    ElecBalanceSerializer,
    ElecOperationInputSerializer,
    ElecOperationListSerializer,
    ElecOperationUpdateSerializer,
)


class ElecOperationListSerializerTest(TestCase):
    """Tests for ElecOperationListSerializer type rendering."""

    def setUp(self):
        self.entity = Entity.objects.create(name="Operator", entity_type=Entity.OPERATOR)
        self.other_entity = Entity.objects.create(name="Other", entity_type=Entity.OPERATOR)

    def test_type_returns_acquisition_when_cession_credited_to_entity(self):
        """Should display ACQUISITION when entity receives a CESSION."""
        operation = ElecOperation.objects.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.PENDING,
            credited_entity=self.entity,
            debited_entity=self.other_entity,
            quantity=500,
        )

        serializer = ElecOperationListSerializer(operation, context={"entity_id": self.entity.id})

        self.assertEqual(serializer.data["type"], ElecOperation.ACQUISITION)

    def test_type_preserves_original_when_not_acquisition(self):
        """Should keep original type when entity is not the credited CESSION target."""
        operation = ElecOperation.objects.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.PENDING,
            credited_entity=self.other_entity,
            debited_entity=self.entity,
            quantity=500,
        )

        serializer = ElecOperationListSerializer(operation, context={"entity_id": self.entity.id})

        self.assertEqual(serializer.data["type"], ElecOperation.CESSION)


class ElecOperationInputSerializerTest(TestCase):
    """Tests for ElecOperationInputSerializer.create()."""

    def setUp(self):
        self.entity = Entity.objects.create(name="Debited", entity_type=Entity.OPERATOR)
        self.other_entity = Entity.objects.create(name="Other", entity_type=Entity.OPERATOR)
        self.mock_request = Mock()
        self.mock_request.entity = self.entity

    def test_raises_when_debited_entity_differs_from_request_entity(self):
        """Should raise ValidationError if debited_entity != request.entity."""
        serializer = ElecOperationInputSerializer(context={"request": self.mock_request})
        validated_data = {
            "type": ElecOperation.CESSION,
            "credited_entity": self.other_entity,
            "debited_entity": self.other_entity,
            "quantity": 100,
        }

        with self.assertRaises(serializers.ValidationError):
            serializer.create(validated_data)

    @patch("tiruert.serializers.elec_operation.ElecOperationService")
    def test_calls_service_and_creates_operation(self, mock_service):
        """Should call perform_checks_before_create and persist operation."""
        mock_service.perform_checks_before_create.return_value = None
        serializer = ElecOperationInputSerializer(context={"request": self.mock_request})
        validated_data = {
            "type": ElecOperation.CESSION,
            "credited_entity": self.other_entity,
            "debited_entity": self.entity,
            "quantity": 150,
        }

        operation = serializer.create(validated_data)

        mock_service.perform_checks_before_create.assert_called_once_with(self.mock_request, validated_data)
        self.assertIsNotNone(operation.id)
        self.assertEqual(operation.debited_entity, self.entity)
        self.assertEqual(operation.credited_entity, self.other_entity)
        self.assertEqual(operation.quantity, 150)


class ElecOperationUpdateSerializerTest(TestCase):
    """Tests for ElecOperationUpdateSerializer.update()."""

    def setUp(self):
        self.entity = Entity.objects.create(name="Debited", entity_type=Entity.OPERATOR)
        self.other_entity = Entity.objects.create(name="Other", entity_type=Entity.OPERATOR)
        self.request = Mock()
        self.request.entity = self.entity

    def _serializer(self, instance, data):
        return ElecOperationUpdateSerializer(instance, data=data, context={"request": self.request}, partial=True)

    def test_raises_when_debited_entity_differs_from_request_entity(self):
        """Should raise when current debited_entity is not request.entity."""
        instance = ElecOperation.objects.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.PENDING,
            credited_entity=self.other_entity,
            debited_entity=self.other_entity,
            quantity=100,
        )
        serializer = self._serializer(instance, {"quantity": 200})

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def test_raises_when_type_not_allowed(self):
        """Should raise for non-editable types."""
        instance = ElecOperation.objects.create(
            type=ElecOperation.ACQUISITION_FROM_CPO,
            status=ElecOperation.PENDING,
            credited_entity=self.other_entity,
            debited_entity=self.entity,
            quantity=100,
        )
        serializer = self._serializer(instance, {"quantity": 200})

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def test_raises_when_status_not_allowed(self):
        """Should raise when status not in editable statuses."""
        instance = ElecOperation.objects.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.ACCEPTED,
            credited_entity=self.other_entity,
            debited_entity=self.entity,
            quantity=100,
        )
        serializer = self._serializer(instance, {"quantity": 200})

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def test_raises_when_attempting_to_change_debited_entity(self):
        """Should raise when debited_entity is modified."""
        instance = ElecOperation.objects.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.PENDING,
            credited_entity=self.other_entity,
            debited_entity=self.entity,
            quantity=100,
        )
        serializer = self._serializer(instance, {"debited_entity": self.other_entity})

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()

    @patch("tiruert.serializers.elec_operation.ElecOperationService")
    def test_calls_service_and_updates(self, mock_service):
        """Should call perform_checks_before_create and apply updates."""
        mock_service.perform_checks_before_create.return_value = None
        instance = ElecOperation.objects.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.PENDING,
            credited_entity=self.other_entity,
            debited_entity=self.entity,
            quantity=100,
        )
        serializer = self._serializer(instance, {"quantity": 250})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()

        mock_service.perform_checks_before_create.assert_called_once()
        self.assertEqual(updated.quantity, 250)


class ElecBalanceSerializerTest(TestCase):
    """Tests for ElecBalanceSerializer.get_initial_balance()."""

    def test_initial_balance_calculates_from_available_and_flows(self):
        """Should compute available - credit + debit."""
        balance = {
            "sector": ElecOperation.SECTOR,
            "available_balance": 1000,
            "quantity": {"credit": 600, "debit": 200},
            "pending_teneur": 50,
            "declared_teneur": 20,
            "pending_operations": 2,
        }

        serializer = ElecBalanceSerializer(balance)

        self.assertEqual(serializer.data["initial_balance"], 600)
