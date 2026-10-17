from django.test import SimpleTestCase

from h2.handlers.action import H2ActionHandler
from h2.permissions import HasH2AdminRights
from traceability.lifecycle.checks import can_change_status, can_create
from traceability.models import Action, ActionStatus


class H2LifecycleTest(SimpleTestCase):
    def setUp(self):
        self.handler = H2ActionHandler()

    def test_pending_init_can_become_accepted_or_rejected(self):
        accepted = can_change_status(self.handler, Action.INIT, ActionStatus.PENDING, ActionStatus.ACCEPTED)
        rejected = can_change_status(self.handler, Action.INIT, ActionStatus.PENDING, ActionStatus.REJECTED)

        self.assertEqual(accepted.to_status, ActionStatus.ACCEPTED)
        self.assertEqual(accepted.permission, HasH2AdminRights)
        self.assertEqual(rejected.to_status, ActionStatus.REJECTED)
        self.assertEqual(rejected.permission, HasH2AdminRights)

    def test_refuses_unknown_status_edges(self):
        self.assertIsNone(can_change_status(self.handler, Action.INIT, ActionStatus.CREATED, ActionStatus.ACCEPTED))
        self.assertIsNone(can_change_status(self.handler, Action.INIT, ActionStatus.ACCEPTED, ActionStatus.ACCEPTED))
        self.assertIsNone(can_change_status(self.handler, Action.VALORIZE, ActionStatus.PENDING, ActionStatus.ACCEPTED))

    def test_creation_rights(self):
        self.assertEqual(can_create(self.handler, Action.INIT).action_type, Action.INIT)
        self.assertIsNone(can_create(self.handler, Action.INIT, parent_type=Action.INIT))
        self.assertIsNone(can_create(self.handler, Action.VALORIZE))
        self.assertEqual(can_create(self.handler, Action.VALORIZE, parent_type=Action.INIT).action_type, Action.VALORIZE)
