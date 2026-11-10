from decimal import Decimal

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from traceability.factories import ActionFactory, MaterialFactory
from traceability.models import Action, ActionStatus, Material
from traceability.services.inherited_fields import annotate_inherited_fields, attach_inherited_fields
from traceability.services.quantities import attach_quantities, attach_quantity_available, convert_quantity


class ConvertQuantityTest(TestCase):
    def test_converts_from_kg(self):
        material = Material(unit=Material.KG, lhv=Decimal("120"), density=Decimal("0.8"))

        self.assertEqual(
            convert_quantity(Decimal("100"), material),
            (Decimal("100.000"), Decimal("125.000"), Decimal("12000.000")),
        )

    def test_missing_factors_leave_derived_values_empty(self):
        kg = Material(unit=Material.KG, lhv=None, density=None)
        litre = Material(unit=Material.L, lhv=None, density=None)
        mj = Material(unit=Material.MJ, lhv=None, density=None)

        self.assertEqual(convert_quantity(Decimal("100"), kg), (Decimal("100.000"), None, None))
        self.assertEqual(convert_quantity(Decimal("50"), litre), (None, Decimal("50.000"), None))
        self.assertEqual(convert_quantity(Decimal("12000"), mj), (None, None, Decimal("12000.000")))

    def test_converts_from_litre(self):
        material = Material(unit=Material.L, lhv=Decimal("120"), density=Decimal("0.8"))

        self.assertEqual(
            convert_quantity(Decimal("50"), material),
            (Decimal("40.000"), Decimal("50.000"), Decimal("4800.000")),
        )

    def test_converts_from_mj(self):
        material = Material(unit=Material.MJ, lhv=Decimal("120"), density=Decimal("0.8"))

        self.assertEqual(
            convert_quantity(Decimal("12000"), material),
            (Decimal("100.000"), Decimal("125.000"), Decimal("12000.000")),
        )

    def test_missing_material_leaves_every_value_empty(self):
        self.assertEqual(convert_quantity(Decimal("100"), None), (None, None, None))


class AttachQuantitiesTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_uses_previous_material_when_the_action_stores_none(self):
        material = MaterialFactory.create(unit=Material.KG, lhv=Decimal("120"), density=Decimal("0.8"))
        parent = ActionFactory.create(type=Action.INIT, quantity=Decimal("100.000"), material=material, parent=None)
        child = ActionFactory.create(type=Action.VALORIZE, quantity=Decimal("100.000"), material=None, parent=parent)

        resolved = list(annotate_inherited_fields(Action.objects.filter(pk=child.pk)))
        attach_quantities(attach_inherited_fields(resolved))

        self.assertEqual(resolved[0].mass, Decimal("100.000"))
        self.assertEqual(resolved[0].volume, Decimal("125.000"))
        self.assertEqual(resolved[0].energy, Decimal("12000.000"))

    def test_stored_material_wins_over_previous_material(self):
        parent = ActionFactory.create(
            type=Action.INIT,
            quantity=Decimal("10.000"),
            material=MaterialFactory.create(unit=Material.KG, lhv=Decimal("120"), density=Decimal("0.8")),
            parent=None,
        )
        child = ActionFactory.create(
            type=Action.INIT,
            quantity=Decimal("50.000"),
            material=MaterialFactory.create(unit=Material.L, lhv=Decimal("120"), density=Decimal("0.8")),
            parent=parent,
        )

        resolved = list(annotate_inherited_fields(Action.objects.filter(pk=child.pk)))
        attach_quantities(attach_inherited_fields(resolved))

        self.assertEqual(resolved[0].mass, Decimal("40.000"))
        self.assertEqual(resolved[0].volume, Decimal("50.000"))
        self.assertEqual(resolved[0].energy, Decimal("4800.000"))


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
        self.assertEqual(child.quantity_available, Decimal("-20.000"))

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
