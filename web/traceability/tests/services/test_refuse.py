from django.test import TestCase

from traceability.exceptions import NoEligibleActionError
from traceability.factories import ActionFactory
from traceability.models import Action, ActionStatus
from traceability.services.refuse import refuse


class RefuseTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_rejects_pending_init(self):
        action = ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None)
        ActionStatus.objects.create(action=action, status=ActionStatus.PENDING)

        refused = refuse(Action.objects.filter(pk=action.pk))

        self.assertEqual(len(refused), 1)
        self.assertEqual(refused[0].pk, action.pk)
        self.assertEqual(Action.objects.get(pk=action.pk).status, ActionStatus.REJECTED)

    def test_skips_ineligible_actions(self):
        pending = ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None)
        ActionStatus.objects.create(action=pending, status=ActionStatus.PENDING)
        ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None, status=ActionStatus.CREATED)
        ActionFactory.create(type=Action.VALORIZE, industry=Action.H2, parent=None, status=ActionStatus.PENDING)

        refused = refuse(Action.objects.all())

        self.assertEqual(len(refused), 1)
        self.assertEqual(refused[0].pk, pending.pk)
        self.assertEqual(Action.objects.get(pk=pending.pk).status, ActionStatus.REJECTED)

    def test_raises_when_nothing_is_eligible(self):
        ActionFactory.create(type=Action.INIT, industry=Action.H2, parent=None, status=ActionStatus.CREATED)

        with self.assertRaises(NoEligibleActionError):
            refuse(Action.objects.all())
