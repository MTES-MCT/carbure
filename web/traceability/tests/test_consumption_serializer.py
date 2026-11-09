from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.validators import UniqueValidator

from traceability.models import Action
from traceability.serializers.consumption import ConsumptionSerializer


class ConsumptionSerializerTest(SimpleTestCase):
    def test_validates_consumption_and_sets_its_type(self):
        serializer = ConsumptionSerializer(
            data={
                "type": Action.VALORIZE,
                "pos_id": "POS-1",
                "quantity": "12.500",
                "working_date": "2026-01-01",
                "material": None,
                "site": None,
            }
        )

        with patch.object(UniqueValidator, "__call__", return_value=None):
            self.assertTrue(serializer.is_valid(), serializer.errors)

        self.assertEqual(serializer.validated_data["type"], Action.INIT)
        self.assertEqual(str(serializer.validated_data["quantity"]), "12.500")

    def test_rejects_missing_or_invalid_required_data(self):
        serializer = ConsumptionSerializer(data={"quantity": "not a number"})

        self.assertFalse(serializer.is_valid())
        self.assertIn("pos_id", serializer.errors)
        self.assertIn("quantity", serializer.errors)
        self.assertIn("working_date", serializer.errors)
