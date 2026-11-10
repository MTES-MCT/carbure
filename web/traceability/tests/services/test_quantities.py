from decimal import Decimal

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from traceability.factories import ActionFactory
from traceability.models import Action, ActionStatus
from traceability.services.quantities import quantity_available


def available(*actions):
    rows = (
        Action.unannotated.filter(pk__in=[action.pk for action in actions])
        .annotate(quantity_available=quantity_available())
        .values_list("pk", "quantity_available")
    )
    return dict(rows)


class QuantityAvailableTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_without_children_the_available_quantity_is_the_action_quantity(self):
        action = ActionFactory.create(quantity=Decimal("100.000"))

        self.assertEqual(available(action)[action.pk], Decimal("100.000"))

    def test_subtracts_direct_children_and_ignores_grandchildren(self):
        parent = ActionFactory.create(quantity=Decimal("100.000"), parent=None)
        child = ActionFactory.create(quantity=Decimal("30.000"), parent=parent)
        ActionFactory.create(quantity=Decimal("50.000"), parent=child)

        values = available(parent, child)

        self.assertEqual(values[parent.pk], Decimal("70.000"))

    def test_deleted_and_rejected_children_do_not_consume_the_parent(self):
        parent = ActionFactory.create(quantity=Decimal("100.000"), parent=None)
        ActionFactory.create(quantity=Decimal("40.000"), parent=parent, status=ActionStatus.PENDING)
        ActionFactory.create(quantity=Decimal("25.000"), parent=parent, status=ActionStatus.DELETED)
        ActionFactory.create(quantity=Decimal("15.000"), parent=parent, status=ActionStatus.REJECTED)

        self.assertEqual(available(parent)[parent.pk], Decimal("60.000"))

    def test_only_the_latest_status_decides(self):
        parent = ActionFactory.create(quantity=Decimal("100.000"), parent=None)
        released = ActionFactory.create(quantity=Decimal("10.000"), parent=parent, status=ActionStatus.DELETED)
        removed = ActionFactory.create(quantity=Decimal("30.000"), parent=parent, status=ActionStatus.CREATED)
        ActionStatus.objects.create(action=released, status=ActionStatus.ACCEPTED)
        ActionStatus.objects.create(action=removed, status=ActionStatus.DELETED)

        self.assertEqual(available(parent)[parent.pk], Decimal("90.000"))

    def test_queries_only_the_given_actions(self):
        parent = ActionFactory.create(quantity=Decimal("10.000"), parent=None)
        ActionFactory.create(quantity=Decimal("1.000"), parent=parent)
        other = ActionFactory.create(quantity=Decimal("10.000"), parent=None)
        ActionFactory.create(quantity=Decimal("9.000"), parent=other)

        with CaptureQueriesContext(connection) as captured:
            values = available(parent)

        self.assertEqual(len(captured), 1)
        self.assertEqual(values[parent.pk], Decimal("9.000"))
        self.assertNotIn(other.pk, values)

    def test_the_manager_drops_a_fully_consumed_action(self):
        kept = ActionFactory.create(quantity=Decimal("100.000"), parent=None)
        exhausted = ActionFactory.create(quantity=Decimal("30.000"), parent=None)
        ActionFactory.create(quantity=Decimal("30.000"), parent=exhausted)
        untouched = ActionFactory.create(quantity=Decimal("10.000"), parent=None)

        ids = set(Action.objects.values_list("id", flat=True))

        self.assertIn(kept.id, ids)
        self.assertIn(untouched.id, ids)
        self.assertNotIn(exhausted.id, ids)
