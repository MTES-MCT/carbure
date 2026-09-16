from decimal import Decimal

from django.test import TestCase

from traceability.factories import ActionFactory, MaterialFactory
from traceability.models import Action


class AnnotateQuantitiesTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_manager_annotates_mass_volume_energy_from_action_factors(self):
        material = MaterialFactory.create(lhv=Decimal("999"), density=Decimal("9"))
        action = ActionFactory.create(
            type=Action.INIT,
            unit=Action.KG,
            quantity=Decimal("100.000"),
            material=material,
            lhv=Decimal("120"),
            density=Decimal("0.8"),
        )

        annotated = Action.objects.get(pk=action.pk)
        self.assertEqual(annotated.mass, Decimal("100.000"))
        self.assertEqual(annotated.volume, Decimal("125.000"))
        self.assertEqual(annotated.energy, Decimal("12000.000"))

    def test_missing_factors_leave_derived_values_null(self):
        kg = ActionFactory.create(type=Action.INIT, unit=Action.KG, quantity=Decimal("100.000"), lhv=None, density=None)
        litre = ActionFactory.create(type=Action.INIT, unit=Action.L, quantity=Decimal("50.000"), lhv=None, density=None)
        mj = ActionFactory.create(
            type=Action.VALORIZE, unit=Action.MJ, quantity=Decimal("12000.000"), material=None, lhv=None, density=None
        )

        annotated_kg = Action.objects.get(pk=kg.pk)
        self.assertEqual(annotated_kg.mass, Decimal("100.000"))
        self.assertIsNone(annotated_kg.volume)
        self.assertIsNone(annotated_kg.energy)

        annotated_litre = Action.objects.get(pk=litre.pk)
        self.assertIsNone(annotated_litre.mass)
        self.assertEqual(annotated_litre.volume, Decimal("50.000"))
        self.assertIsNone(annotated_litre.energy)

        annotated_mj = Action.objects.get(pk=mj.pk)
        self.assertIsNone(annotated_mj.mass)
        self.assertIsNone(annotated_mj.volume)
        self.assertEqual(annotated_mj.energy, Decimal("12000.000"))
