from decimal import Decimal
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from traceability.models import Action
from traceability.serializers.valorize import ValorizeSerializer


class ValorizeSerializerTest(SimpleTestCase):
    def test_only_requires_parent_and_sets_its_type(self):
        parent = Action(id=1, quantity=Decimal("12.500"))
        queryset = Mock()
        queryset.get.return_value = parent
        serializer = ValorizeSerializer(
            data={"parent": parent.pk, "type": Action.INIT, "quantity": "999", "pos_id": "CLIENT-POS"}
        )

        with patch.object(serializer.fields["parent"], "get_queryset", return_value=queryset):
            self.assertTrue(serializer.is_valid(), serializer.errors)

        self.assertEqual(serializer.validated_data, {"type": Action.VALORIZE, "parent": parent})

    def test_rejects_missing_or_null_parent(self):
        for data in ({}, {"parent": None}):
            with self.subTest(data=data):
                serializer = ValorizeSerializer(data=data)

                self.assertFalse(serializer.is_valid())
                self.assertIn("parent", serializer.errors)
