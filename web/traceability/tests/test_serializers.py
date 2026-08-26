from types import SimpleNamespace

from django.forms.models import model_to_dict
from django.test import TestCase

from core.models import Entity
from traceability.factories import ActionFactory
from traceability.models import Action
from traceability.serializers import ActionInputSerializer


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
