from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from rest_framework.validators import UniqueValidator

from traceability.models import Action
from traceability.serializers.consumption import ConsumptionSerializer


class ConsumptionSerializerTest(SimpleTestCase):
    def setUp(self):
        self.entity = object()
        self.material = SimpleNamespace(name="Hydrogène gazeux")
        self.certificate = SimpleNamespace(certificate_id="CHY-001")
        self.site = SimpleNamespace(name="Station Paris")
        self.lookups = SimpleNamespace(
            material=Mock(return_value=[self.material]),
            certificate=Mock(return_value=[self.certificate]),
            site=Mock(return_value=[self.site]),
        )
        self.context = {"handler": SimpleNamespace(lookups=self.lookups), "entity": self.entity}
        self.payload = {
            "pos_id": "POS-1",
            "quantity": "12.500",
            "working_date": "2026-01-01",
            "material": self.material.name,
            "certificate": self.certificate.certificate_id,
            "site": self.site.name,
        }

    def test_resolves_relations_using_handler_lookups(self):
        serializer = ConsumptionSerializer(data=self.payload, context=self.context)

        with patch.object(UniqueValidator, "__call__", return_value=None):
            self.assertTrue(serializer.is_valid(), serializer.errors)

        for field in ("material", "certificate", "site"):
            with self.subTest(field=field):
                self.assertIs(serializer.validated_data[field], getattr(self, field))
                getattr(self.lookups, field).assert_called_once_with(self.entity)

    def test_rejects_relations_outside_handler_lookups(self):
        for field in ("material", "certificate", "site"):
            with self.subTest(field=field):
                serializer = ConsumptionSerializer(
                    data={**self.payload, field: "unknown"},
                    context={**self.context, "serializer_cache": {}},
                )

                with patch.object(UniqueValidator, "__call__", return_value=None):
                    self.assertFalse(serializer.is_valid())

                self.assertEqual(set(serializer.errors), {field})
                self.assertEqual(serializer.errors[field][0].code, "does_not_exist")

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
