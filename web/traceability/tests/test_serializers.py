from django.test import TestCase

from core.models import Entity
from traceability.factories import ActionFactory
from traceability.serializers import ActionInputSerializer, ActionSerializer


class ActionSerializerTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_relations_are_nested_when_reading_an_action(self):
        holder = Entity.objects.create(name="Holder", entity_type=Entity.HRS)
        parent = ActionFactory.create(holder=holder)
        action = ActionFactory.create(holder=holder, parent=parent)

        data = ActionSerializer(action).data

        self.assertEqual(
            data["holder"],
            {
                "id": holder.id,
                "name": holder.name,
                "entity_type": holder.entity_type,
                "registration_id": holder.registration_id,
            },
        )
        self.assertEqual(
            data["parent"],
            {"id": parent.id, "pos_id": parent.pos_id},
        )
        self.assertEqual(
            data["material"],
            {"id": action.material.id, "code": action.material.code, "name": action.material.name},
        )
        self.assertEqual(
            data["site"],
            {"id": action.site.id, "name": action.site.name, "site_type": action.site.site_type},
        )

    def test_relations_remain_ids_when_writing_an_action(self):
        action = ActionFactory.create()

        data = ActionInputSerializer(action).data

        self.assertEqual(data["holder"], action.holder.id)
        self.assertEqual(data["industry"], action.industry)
        self.assertEqual(data["parent"], action.parent_id)
        self.assertEqual(data["material"], action.material.id)
        self.assertEqual(data["site"], action.site.id)
