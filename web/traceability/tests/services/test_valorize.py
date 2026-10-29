from decimal import Decimal

from django.test import TestCase

from traceability.exceptions import NoEligibleActionError
from traceability.factories import ActionFactory, MaterialFactory
from traceability.models import Action, ActionStatus, Material
from traceability.services.inherited_fields import annotate_inherited_fields, attach_inherited_fields
from traceability.services.valorize import valorize


class ValorizeTest(TestCase):
    fixtures = ["json/countries.json"]

    def _pending_init(self, **kwargs):
        action = ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None, **kwargs)
        ActionStatus.objects.create(action=action, status=ActionStatus.PENDING)
        return action

    def test_creates_valorize_child_and_accepts_pending_init(self):
        action = self._pending_init(quantity=Decimal("100.000"), material=MaterialFactory(unit=Material.KG))

        created = valorize(Action.objects.filter(pk=action.pk))

        self.assertEqual(len(created), 1)
        child = created[0]
        self.assertEqual(child.type, Action.VALORIZE)
        self.assertEqual(child.parent_id, action.pk)
        self.assertEqual(child.holder_id, action.holder_id)
        self.assertIsNone(child.material_id)
        self.assertEqual(child.quantity, action.quantity)
        self.assertEqual(Action.objects.with_status().get(pk=action.pk).status, ActionStatus.ACCEPTED)

    def test_displayed_unit_is_the_parent_material(self):
        action = self._pending_init(
            quantity=Decimal("50.000"),
            material=MaterialFactory(unit=Material.L, lhv=None, density=None),
        )

        created = valorize(Action.objects.filter(pk=action.pk))

        child = annotate_inherited_fields(Action.objects.filter(pk=created[0].pk)).get()
        attach_inherited_fields([child])
        self.assertEqual(child.quantity, Decimal("50.000"))
        self.assertIsNone(child.material_id)
        self.assertEqual(child.inherited_fields["previous_material"].pk, action.material_id)
        self.assertEqual(child.inherited_fields["previous_material"].unit, Material.L)
        self.assertEqual(child.inherited_fields["origin_material"].pk, action.material_id)

    def test_skips_ineligible_actions(self):
        pending = self._pending_init()
        ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None, status=ActionStatus.CREATED)

        created = valorize(Action.objects.filter(type=Action.INIT))

        self.assertEqual(len(created), 1)
        self.assertEqual(created[0].parent_id, pending.pk)
        self.assertEqual(created[0].quantity, pending.quantity)

    def test_raises_when_nothing_is_eligible(self):
        ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None, status=ActionStatus.CREATED)

        with self.assertRaises(NoEligibleActionError):
            valorize(Action.objects.all())
