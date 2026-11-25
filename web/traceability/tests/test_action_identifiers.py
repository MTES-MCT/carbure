from datetime import date
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase

from traceability.factories import ActionFactory
from traceability.models import Action
from traceability.models.action import Industry
from traceability.serializers.action import ActionParentSerializer


def carbure_prefix(action):
    return f"C{action.created_at.year}-{action.industry}-"


class ActionIdentifierTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_annotation_matches_the_base36_label(self):
        action = ActionFactory.create(id=36, industry=Industry.H2)
        annotated = Action.objects.get(pk=action.pk)

        self.assertEqual(annotated.carbure_id, f"C{annotated.created_at.year}-H2-00000010")

    def test_created_at_is_set_on_save_and_kept(self):
        action = ActionFactory.create(pos_id="POS-1")
        fetched = Action.objects.get(pk=action.pk)

        self.assertIsNotNone(fetched.created_at)
        self.assertTrue(fetched.carbure_id.startswith(carbure_prefix(fetched)))
        self.assertEqual(fetched.pos_id, "POS-1")

        created_at = fetched.created_at
        fetched.save()
        fetched = Action.objects.get(pk=action.pk)
        self.assertEqual(fetched.created_at, created_at)
        self.assertTrue(fetched.carbure_id.startswith(carbure_prefix(fetched)))

    def test_blank_pos_id_is_stored_as_null(self):
        action = ActionFactory.create(pos_id="POS-BLANK")
        action.pos_id = ""
        action.save()
        action = Action.objects.get(pk=action.pk)

        self.assertIsNone(action.pos_id)
        self.assertTrue(action.carbure_id.startswith(carbure_prefix(action)))

    def test_several_actions_can_omit_pos_id(self):
        first = ActionFactory.create(pos_id=None)
        second = ActionFactory.create(pos_id="")
        first = Action.objects.get(pk=first.pk)
        second = Action.objects.get(pk=second.pk)

        self.assertIsNone(first.pos_id)
        self.assertIsNone(second.pos_id)
        self.assertTrue(first.carbure_id.startswith(carbure_prefix(first)))
        self.assertTrue(second.carbure_id.startswith(carbure_prefix(second)))
        self.assertNotEqual(first.carbure_id, second.carbure_id)

    def test_parent_serializer_omits_carbure_id(self):
        parent = ActionFactory.create(pos_id="POS-PARENT")
        child = Action.objects.get(pk=ActionFactory.create(pos_id="POS-CHILD", parent=parent).pk)

        self.assertTrue(child.carbure_id.startswith(carbure_prefix(child)))
        self.assertNotIn("carbure_id", ActionParentSerializer(child.parent).data)

    def test_pos_id_stays_unique_when_set(self):
        ActionFactory.create(pos_id="POS-UNIQUE")
        duplicate = ActionFactory.create(pos_id="POS-OTHER")
        duplicate.pos_id = "POS-UNIQUE"

        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate.save()

    def test_bulk_create_assigns_carbure_id_without_pos_id(self):
        holder = ActionFactory.create(pos_id="POS-HOLDER").holder
        created = list(
            Action.bulk_create(
                [
                    Action(
                        pos_id="",
                        holder=holder,
                        industry=Industry.H2,
                        type=Action.INIT,
                        working_date=date(2026, 1, 1),
                        quantity=Decimal("1.000"),
                    ),
                    Action(
                        pos_id=None,
                        holder=holder,
                        industry=Industry.H2,
                        type=Action.INIT,
                        working_date=date(2026, 1, 1),
                        quantity=Decimal("2.000"),
                    ),
                ]
            )
        )

        self.assertEqual(len(created), 2)
        self.assertEqual({action.pos_id for action in created}, {None})
        self.assertTrue(all(action.carbure_id.startswith(carbure_prefix(action)) for action in created))
        self.assertNotEqual(created[0].carbure_id, created[1].carbure_id)
