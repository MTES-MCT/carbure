from django.test import TestCase

from traceability.factories import ActionFactory
from traceability.models import Action, ActionStatus
from traceability.services.valorize import NoEligibleActionError, valorize


class ValorizeTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_creates_valorize_child_and_accepts_pending_init(self):
        action = ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None)
        ActionStatus.objects.create(action=action, status=ActionStatus.PENDING)

        created = valorize(Action.objects.filter(pk=action.pk))

        self.assertEqual(len(created), 1)
        child = created[0]
        self.assertEqual(child.type, Action.VALORIZE)
        self.assertEqual(child.parent_id, action.pk)
        self.assertEqual(child.holder_id, action.holder_id)
        self.assertEqual(child.quantity, action.quantity)
        self.assertEqual(Action.objects.get(pk=action.pk).status, ActionStatus.ACCEPTED)

    def test_skips_ineligible_actions(self):
        pending = ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None)
        ActionStatus.objects.create(action=pending, status=ActionStatus.PENDING)
        ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None, status=ActionStatus.CREATED)

        created = valorize(Action.objects.filter(type=Action.INIT))

        self.assertEqual(len(created), 1)
        self.assertEqual(created[0].parent_id, pending.pk)

    def test_raises_when_nothing_is_eligible(self):
        ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None, status=ActionStatus.CREATED)

        with self.assertRaises(NoEligibleActionError):
            valorize(Action.objects.all())
