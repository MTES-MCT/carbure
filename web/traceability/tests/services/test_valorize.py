from decimal import Decimal

from django.test import TestCase

from traceability.exceptions import ConversionError, NoEligibleActionError
from traceability.factories import ActionFactory, MaterialFactory
from traceability.models import Action, ActionStatus, Material
from traceability.services.valorize import valorize


class ValorizeTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        Material.objects.create(
            code=Material.VALORIZED_ENERGY_CODE,
            name=Material.VALORIZED_ENERGY_NAME,
            unit=Material.MJ,
        )

    def _pending_init(self, **kwargs):
        action = ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None, **kwargs)
        ActionStatus.objects.create(action=action, status=ActionStatus.PENDING)
        return action

    def _with_lhv(self, action, lhv=Decimal("120")):
        action.material.lhv = lhv
        action.material.save(update_fields=["lhv"])
        return action

    def test_creates_valorize_child_and_accepts_pending_init(self):
        action = self._with_lhv(self._pending_init(quantity=Decimal("100.000")))

        created = valorize(Action.objects.filter(pk=action.pk))

        self.assertEqual(len(created), 1)
        child = created[0]
        self.assertEqual(child.type, Action.VALORIZE)
        self.assertEqual(child.parent_id, action.pk)
        self.assertEqual(child.holder_id, action.holder_id)
        self.assertEqual(child.material_id, Material.valorized_energy().pk)
        self.assertEqual(child.material.unit, Material.MJ)
        self.assertEqual(child.quantity, Decimal("12000.000"))
        self.assertEqual(child.energy, Decimal("12000.000"))
        self.assertIsNone(child.mass)
        self.assertIsNone(child.volume)
        self.assertEqual(Action.objects.get(pk=action.pk).status, ActionStatus.ACCEPTED)

    def test_skips_ineligible_actions(self):
        pending = self._with_lhv(self._pending_init())
        ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None, status=ActionStatus.CREATED)

        created = valorize(Action.objects.filter(type=Action.INIT))

        self.assertEqual(len(created), 1)
        self.assertEqual(created[0].parent_id, pending.pk)

    def test_raises_when_nothing_is_eligible(self):
        ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None, status=ActionStatus.CREATED)

        with self.assertRaises(NoEligibleActionError):
            valorize(Action.objects.all())

    def test_raises_when_energy_cannot_be_converted(self):
        action = self._pending_init(material=MaterialFactory(lhv=None))

        with self.assertRaises(ConversionError) as ctx:
            valorize(Action.objects.filter(pk=action.pk))

        self.assertEqual(ctx.exception.actions, [action])
        self.assertEqual(Action.objects.filter(type=Action.VALORIZE).count(), 0)
        self.assertEqual(Action.objects.get(pk=action.pk).status, ActionStatus.PENDING)

    def test_conversion_error_aborts_the_whole_batch(self):
        convertible = self._with_lhv(self._pending_init())
        blocked = self._pending_init(material=MaterialFactory(lhv=None))

        with self.assertRaises(ConversionError) as ctx:
            valorize(Action.objects.filter(pk__in=[convertible.pk, blocked.pk]))

        self.assertEqual(ctx.exception.actions, [blocked])
        self.assertEqual(Action.objects.filter(type=Action.VALORIZE).count(), 0)
        self.assertEqual(Action.objects.get(pk=convertible.pk).status, ActionStatus.PENDING)

    def test_valorizes_litre_init_using_converted_energy(self):
        action = self._pending_init(
            quantity=Decimal("50.000"),
            material=MaterialFactory(unit=Material.L, lhv=Decimal("120"), density=Decimal("0.8")),
        )

        created = valorize(Action.objects.filter(pk=action.pk))

        child = created[0]
        self.assertEqual(child.material.unit, Material.MJ)
        self.assertEqual(child.quantity, Decimal("4800.000"))
        self.assertEqual(child.energy, Decimal("4800.000"))
        self.assertIsNone(child.mass)
        self.assertIsNone(child.volume)

    def test_valorizes_mj_init_keeping_quantity(self):
        action = self._pending_init(
            quantity=Decimal("12000.000"),
            material=MaterialFactory(unit=Material.MJ, lhv=Decimal("120"), density=Decimal("0.8")),
        )

        created = valorize(Action.objects.filter(pk=action.pk))

        child = created[0]
        self.assertEqual(child.material.unit, Material.MJ)
        self.assertEqual(child.quantity, Decimal("12000.000"))
        self.assertEqual(child.energy, Decimal("12000.000"))
        self.assertIsNone(child.mass)
        self.assertIsNone(child.volume)
