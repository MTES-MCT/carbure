from decimal import Decimal

from django.test import TestCase

from traceability.factories import ActionFactory, MaterialFactory
from traceability.models import Action, Material
from traceability.services.inherited_fields import annotate_inherited_fields, attach_inherited_fields
from traceability.services.quantities import attach_quantities, convert_quantity


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
