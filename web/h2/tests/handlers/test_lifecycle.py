from types import SimpleNamespace

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
        pending_init = SimpleNamespace(type=Action.INIT, status=ActionStatus.PENDING)

        root = can_create(self.handler, Action.INIT)
        child = can_create(self.handler, Action.VALORIZE, parent=pending_init)

        self.assertEqual(root.action_type, Action.INIT)
        self.assertEqual(root.status, ActionStatus.PENDING)
        self.assertIsNone(can_create(self.handler, Action.INIT, parent=pending_init))
        self.assertIsNone(can_create(self.handler, Action.VALORIZE))
        self.assertEqual(child.action_type, Action.VALORIZE)
        self.assertEqual(child.status, ActionStatus.CREATED)
        self.assertIsNone(
            can_create(
                self.handler,
                Action.VALORIZE,
                parent=SimpleNamespace(type=Action.INIT, status=ActionStatus.ACCEPTED),
            )
        )
        self.assertIsNone(
            can_create(
                self.handler,
                Action.VALORIZE,
                parent=SimpleNamespace(type=Action.VALORIZE, status=ActionStatus.PENDING),
            )
        )
