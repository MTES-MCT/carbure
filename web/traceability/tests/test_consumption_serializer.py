from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from rest_framework.validators import UniqueValidator

from core.models import Entity
from traceability.models import Action, ActionStatus
from traceability.serializers.consumption import ConsumptionSerializer


class ConsumptionSerializerTest(SimpleTestCase):
    def setUp(self):
        self.entity = Entity(id=1)
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
            "type": Action.INIT,
            "status": ActionStatus.PENDING,
            "holder": self.entity.pk,
            "pos_id": "POS-1",
            "quantity": "12.500",
            "working_date": "2026-01-01",
            "material": self.material.name,
            "certificate": self.certificate.certificate_id,
            "site": self.site.name,
        }

    def validate(self, serializer):
        queryset = Mock()
        queryset.get.return_value = self.entity
        with (
            patch.object(serializer.fields["holder"], "get_queryset", return_value=queryset),
            patch.object(UniqueValidator, "__call__", return_value=None),
        ):
            return serializer.is_valid()

    def test_resolves_relations_using_handler_lookups(self):
        serializer = ConsumptionSerializer(data=self.payload, context=self.context)

        self.assertTrue(self.validate(serializer), serializer.errors)

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

                self.assertFalse(self.validate(serializer))

                self.assertEqual(set(serializer.errors), {field})
                self.assertEqual(serializer.errors[field][0].code, "does_not_exist")

    def test_validates_complete_consumption_request(self):
        serializer = ConsumptionSerializer(
            data={
                **self.payload,
                "material": None,
                "certificate": None,
                "site": None,
            }
        )

        self.assertTrue(self.validate(serializer), serializer.errors)

        self.assertEqual(serializer.validated_data["type"], Action.INIT)
        self.assertEqual(str(serializer.validated_data["quantity"]), "12.500")

    def test_rejects_another_action_type(self):
        serializer = ConsumptionSerializer(data={**self.payload, "type": Action.VALORIZE}, context=self.context)

        self.assertFalse(self.validate(serializer))
        self.assertEqual(set(serializer.errors), {"type"})

    def test_rejects_missing_or_invalid_required_data(self):
        serializer = ConsumptionSerializer(data={"quantity": "not a number"})

        self.assertFalse(serializer.is_valid())
        self.assertIn("pos_id", serializer.errors)
        self.assertIn("quantity", serializer.errors)
        self.assertIn("working_date", serializer.errors)
