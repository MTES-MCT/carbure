from decimal import Decimal
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from core.models import Entity
from traceability.models import Action, ActionStatus
from traceability.serializers.valorize import ValorizeSerializer


class ValorizeSerializerTest(SimpleTestCase):
    def setUp(self):
        self.holder = Entity(id=2)
        self.parent = Action(id=1, holder=self.holder, quantity=Decimal("12.500"))
        self.payload = {
            "type": Action.VALORIZE,
            "parent": self.parent.pk,
            "holder": self.holder.pk,
            "status": ActionStatus.CREATED,
        }

    def validate(self, serializer):
        parent_queryset = Mock()
        parent_queryset.get.return_value = self.parent
        holder_queryset = Mock()
        holder_queryset.get.return_value = self.holder
        with (
            patch.object(serializer.fields["parent"], "get_queryset", return_value=parent_queryset),
            patch.object(serializer.fields["holder"], "get_queryset", return_value=holder_queryset),
        ):
            return serializer.is_valid()

    def test_requires_authorization_fields_and_parent_without_consumption_data(self):
        serializer = ValorizeSerializer(data={**self.payload, "quantity": "999", "pos_id": "CLIENT-POS"})

        self.assertTrue(self.validate(serializer), serializer.errors)

        self.assertEqual(
            serializer.validated_data,
            {"type": Action.VALORIZE, "parent": self.parent, "holder": self.holder, "status": ActionStatus.CREATED},
        )

    def test_rejects_another_action_type(self):
        serializer = ValorizeSerializer(data={**self.payload, "type": Action.INIT})

        self.assertFalse(self.validate(serializer))
        self.assertEqual(set(serializer.errors), {"type"})

    def test_rejects_missing_or_null_parent(self):
        payload = {key: value for key, value in self.payload.items() if key != "parent"}
        for data in ({}, {"parent": None}):
            with self.subTest(data=data):
                serializer = ValorizeSerializer(data={**payload, **data})

                self.assertFalse(self.validate(serializer))
                self.assertIn("parent", serializer.errors)
