from decimal import Decimal

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from traceability.factories import ActionFactory
from traceability.models import ActionStatus
from traceability.services.quantities import attach_quantity_available


class AttachQuantityAvailableTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_without_children_the_available_quantity_is_the_action_quantity(self):
        action = ActionFactory.create(quantity=Decimal("100.000"))

        attach_quantity_available([action])

        self.assertEqual(action.quantity_available, Decimal("100.000"))

    def test_subtracts_direct_children_and_ignores_grandchildren(self):
        parent = ActionFactory.create(quantity=Decimal("100.000"), parent=None)
        child = ActionFactory.create(quantity=Decimal("30.000"), parent=parent)
        ActionFactory.create(quantity=Decimal("50.000"), parent=child)

        attach_quantity_available([parent, child])

        self.assertEqual(parent.quantity_available, Decimal("70.000"))

    def test_deleted_and_rejected_children_do_not_consume_the_parent(self):
        parent = ActionFactory.create(quantity=Decimal("100.000"), parent=None)
        ActionFactory.create(quantity=Decimal("40.000"), parent=parent, status=ActionStatus.PENDING)
        ActionFactory.create(quantity=Decimal("25.000"), parent=parent, status=ActionStatus.DELETED)
        ActionFactory.create(quantity=Decimal("15.000"), parent=parent, status=ActionStatus.REJECTED)

        attach_quantity_available([parent])

        self.assertEqual(parent.quantity_available, Decimal("60.000"))

    def test_only_the_latest_status_decides(self):
        parent = ActionFactory.create(quantity=Decimal("100.000"), parent=None)
        released = ActionFactory.create(quantity=Decimal("10.000"), parent=parent, status=ActionStatus.DELETED)
        removed = ActionFactory.create(quantity=Decimal("30.000"), parent=parent, status=ActionStatus.CREATED)
        ActionStatus.objects.create(action=released, status=ActionStatus.ACCEPTED)
        ActionStatus.objects.create(action=removed, status=ActionStatus.DELETED)

        attach_quantity_available([parent])

        self.assertEqual(parent.quantity_available, Decimal("90.000"))

    def test_a_child_without_status_still_counts(self):
        parent = ActionFactory.create(quantity=Decimal("100.000"), parent=None)
        child = ActionFactory.create(quantity=Decimal("20.000"), parent=parent)
        ActionStatus.objects.filter(action=child).delete()

        attach_quantity_available([parent])

        self.assertEqual(parent.quantity_available, Decimal("80.000"))

    def test_queries_only_the_given_actions(self):
        parent = ActionFactory.create(quantity=Decimal("10.000"), parent=None)
        ActionFactory.create(quantity=Decimal("1.000"), parent=parent)
        other = ActionFactory.create(quantity=Decimal("10.000"), parent=None)
        ActionFactory.create(quantity=Decimal("9.000"), parent=other)

        with CaptureQueriesContext(connection) as captured:
            attach_quantity_available([])
        self.assertEqual(len(captured), 0)

        with CaptureQueriesContext(connection) as captured:
            attach_quantity_available([parent])

        self.assertEqual(len(captured), 1)
        self.assertNotIn("JOIN", captured[0]["sql"].upper())
        self.assertEqual(parent.quantity_available, Decimal("9.000"))
        self.assertFalse(hasattr(other, "quantity_available"))
