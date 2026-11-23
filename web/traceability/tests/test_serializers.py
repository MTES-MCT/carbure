from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

from django.forms.models import model_to_dict
from django.test import SimpleTestCase, TestCase
from rest_framework import serializers

from core.models import Entity
from traceability.factories import ActionFactory
from traceability.models import Action
from traceability.serializers import ActionInputSerializer
from traceability.serializers.fields import EMISSION_DECIMAL, LookupSlugRelatedField, TruncatingDecimalField
from traceability.serializers.total_emissions import ActionTotalEmissionsSerializer


class ActionInputSerializerTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.entity = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        self.other_entity = Entity.objects.create(name="Other HRS", entity_type=Entity.HRS)
        self.context = {
            "handler": SimpleNamespace(industry=Action.H2),
            "entity": self.entity,
        }

    def test_create_sets_industry_and_holder_from_context(self):
        payload = model_to_dict(
            ActionFactory.create(holder=self.entity, industry=Action.H2),
            exclude=ActionInputSerializer.Meta.read_only_fields,
        )
        payload["pos_id"] = "POS-CREATE-001"

        serializer = ActionInputSerializer(data=payload, context=self.context)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        created = serializer.save()
        self.assertEqual(created.holder, self.entity)
        self.assertEqual(created.industry, Action.H2)

    def test_read_only_fields_cannot_be_updated(self):
        action = ActionFactory.create(holder=self.entity, industry=Action.H2)
        parent_action = ActionFactory.create(holder=self.entity, industry=Action.H2)

        serializer = ActionInputSerializer(
            action,
            data={
                "id": 99999,
                "industry": "BIOMASS",
                "holder": self.other_entity.id,
                "parent": parent_action.id,
            },
            partial=True,
            context=self.context,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        action.refresh_from_db()
        self.assertNotEqual(action.id, 99999)
        self.assertEqual(action.industry, Action.H2)
        self.assertEqual(action.holder, self.entity)
        self.assertIsNone(action.parent_id)


class LookupSlugRelatedFieldTest(SimpleTestCase):
    def test_get_queryset_is_called_once_when_context_is_shared(self):
        material = SimpleNamespace(name="Hydrogène gazeux")
        context = {}

        first = LookupSlugRelatedField(slug_field="name", lookup="material")
        second = LookupSlugRelatedField(slug_field="name", lookup="material")
        first._context = context
        second._context = context
        first.get_queryset = Mock(return_value=[material])
        second.get_queryset = Mock(return_value=[material])

        self.assertEqual(first.to_internal_value("Hydrogène gazeux"), material)
        self.assertEqual(second.to_internal_value("Hydrogène gazeux"), material)
        first.get_queryset.assert_called_once()
        second.get_queryset.assert_not_called()


class ActionTotalEmissionsSerializerTest(SimpleTestCase):
    def test_represents_a_chain_sum_above_one_post_ceiling(self):
        payload = {name: Decimal("0") for name in ("eec", "el", "ei", "ep", "etd", "eu", "eccs", "esca", "eccr", "total")}
        payload["total"] = Decimal("1000.1234567890")

        self.assertEqual(ActionTotalEmissionsSerializer(payload).data["total"], "1000.1234567890")


class TruncatingDecimalFieldTest(SimpleTestCase):
    def setUp(self):
        self.field = TruncatingDecimalField(max_digits=7, decimal_places=3, min_value=Decimal("0"))

    def test_drops_digits_past_three_decimals(self):
        self.assertEqual(self.field.run_validation("1.2349"), Decimal("1.234"))
        self.assertEqual(self.field.run_validation("1.234"), Decimal("1.234"))

    def test_rejects_a_value_that_still_exceeds_the_digit_limit(self):
        with self.assertRaises(serializers.ValidationError):
            self.field.run_validation("10000.1234")

    def test_drops_excel_float_noise_past_ten_decimals(self):
        field = TruncatingDecimalField(**EMISSION_DECIMAL)

        self.assertEqual(field.run_validation(15.339000000000002), Decimal("15.3390000000"))

    def test_rejects_a_fourth_integer_digit_on_emissions(self):
        field = TruncatingDecimalField(**EMISSION_DECIMAL)

        self.assertEqual(field.run_validation("999.1234567890"), Decimal("999.1234567890"))
        with self.assertRaises(serializers.ValidationError):
            field.run_validation("1000")
