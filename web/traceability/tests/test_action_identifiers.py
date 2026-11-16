from datetime import date
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase

from traceability.factories import ActionFactory
from traceability.models import Action


class ActionIdentifierTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_assigns_a_carbure_id_and_keeps_it(self):
        action = ActionFactory.create(pos_id="POS-1")
        carbure_id = action.carbure_id

        action.save()
        action.refresh_from_db()

        self.assertTrue(carbure_id)
        self.assertEqual(action.carbure_id, carbure_id)
        self.assertEqual(action.pos_id, "POS-1")

    def test_blank_pos_id_is_stored_as_null(self):
        action = ActionFactory.create(pos_id="POS-BLANK")
        action.pos_id = ""
        action.save()
        action.refresh_from_db()

        self.assertIsNone(action.pos_id)
        self.assertTrue(action.carbure_id)

    def test_several_actions_can_omit_pos_id(self):
        first = ActionFactory.create(pos_id="POS-A")
        second = ActionFactory.create(pos_id="POS-B")
        first.pos_id = None
        second.pos_id = ""
        first.save()
        second.save()
        first.refresh_from_db()
        second.refresh_from_db()

        self.assertIsNone(first.pos_id)
        self.assertIsNone(second.pos_id)
        self.assertNotEqual(first.carbure_id, second.carbure_id)

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
        self.assertEqual(len({action.carbure_id for action in created}), 2)
