from datetime import date
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import Value
from django.test import TestCase

from traceability.factories import ActionFactory
from traceability.models import Action
from traceability.models.action import carbure_id_expression
from traceability.serializers.action import ActionParentSerializer


class ActionIdentifierTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_annotation_matches_the_base36_label(self):
        action = ActionFactory.create()
        annotated = (
            Action.objects.filter(pk=action.pk)
            .annotate(
                one=carbure_id_expression(Value(1)),
                ten=carbure_id_expression(Value(10)),
                thirty_six=carbure_id_expression(Value(36)),
                wide=carbure_id_expression(Value(4545757242)),
            )
            .get()
        )

        self.assertEqual(annotated.carbure_id.rsplit("-", 1)[-1], str(action.pk))
        self.assertEqual(annotated.one, "C-00000001-1")
        self.assertEqual(annotated.ten, "C-0000000A-10")
        self.assertEqual(annotated.thirty_six, "C-00000010-36")
        self.assertEqual(annotated.wide, "C-0236FCQI-4545757242")

    def test_carbure_id_is_the_prefixed_primary_key(self):
        action = ActionFactory.create(pos_id="POS-1")
        fetched = Action.objects.get(pk=action.pk)

        self.assertEqual(fetched.carbure_id.rsplit("-", 1)[-1], str(action.pk))
        self.assertEqual(fetched.pos_id, "POS-1")

        fetched.save()
        fetched = Action.objects.get(pk=action.pk)
        self.assertEqual(fetched.carbure_id.rsplit("-", 1)[-1], str(action.pk))

    def test_blank_pos_id_is_stored_as_null(self):
        action = ActionFactory.create(pos_id="POS-BLANK")
        action.pos_id = ""
        action.save()
        action = Action.objects.get(pk=action.pk)

        self.assertIsNone(action.pos_id)
        self.assertEqual(action.carbure_id.rsplit("-", 1)[-1], str(action.pk))

    def test_several_actions_can_omit_pos_id(self):
        first = ActionFactory.create(pos_id=None)
        second = ActionFactory.create(pos_id="")
        first = Action.objects.get(pk=first.pk)
        second = Action.objects.get(pk=second.pk)

        self.assertIsNone(first.pos_id)
        self.assertIsNone(second.pos_id)
        self.assertEqual(first.carbure_id.rsplit("-", 1)[-1], str(first.pk))
        self.assertEqual(second.carbure_id.rsplit("-", 1)[-1], str(second.pk))
        self.assertNotEqual(first.carbure_id, second.carbure_id)

    def test_parent_serializer_omits_carbure_id(self):
        parent = ActionFactory.create(pos_id="POS-PARENT")
        child = Action.objects.get(pk=ActionFactory.create(pos_id="POS-CHILD", parent=parent).pk)

        self.assertEqual(child.carbure_id.rsplit("-", 1)[-1], str(child.pk))
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
                        industry=Action.H2,
                        type=Action.INIT,
                        working_date=date(2026, 1, 1),
                        quantity=Decimal("1.000"),
                    ),
                    Action(
                        pos_id=None,
                        holder=holder,
                        industry=Action.H2,
                        type=Action.INIT,
                        working_date=date(2026, 1, 1),
                        quantity=Decimal("2.000"),
                    ),
                ]
            )
        )

        self.assertEqual(len(created), 2)
        self.assertEqual({action.pos_id for action in created}, {None})
        self.assertEqual(
            [action.carbure_id.rsplit("-", 1)[-1] for action in created],
            [str(action.pk) for action in created],
        )
