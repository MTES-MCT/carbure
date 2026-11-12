from types import SimpleNamespace

from django.test import SimpleTestCase

from h2.handlers.action import H2ActionHandler
from h2.handlers.authorization import can_create_consumption, can_create_valorization
from traceability.lifecycle.checks import can_change_status
from traceability.models import Action, ActionStatus
from traceability.serializers.action_authorization import ActionAuthorizationSerializer

find_edge = ActionAuthorizationSerializer.find_edge


class H2LifecycleTest(SimpleTestCase):
    def setUp(self):
        self.handler = H2ActionHandler()

    def test_pending_init_can_become_accepted_or_rejected(self):
        accepted = can_change_status(self.handler, Action.INIT, ActionStatus.PENDING, ActionStatus.ACCEPTED)
        rejected = can_change_status(self.handler, Action.INIT, ActionStatus.PENDING, ActionStatus.REJECTED)

        self.assertEqual(accepted.to_status, ActionStatus.ACCEPTED)
        self.assertEqual(rejected.to_status, ActionStatus.REJECTED)

    def test_refuses_unknown_status_edges(self):
        self.assertIsNone(can_change_status(self.handler, Action.INIT, ActionStatus.CREATED, ActionStatus.ACCEPTED))
        self.assertIsNone(can_change_status(self.handler, Action.INIT, ActionStatus.ACCEPTED, ActionStatus.ACCEPTED))
        self.assertIsNone(can_change_status(self.handler, Action.VALORIZE, ActionStatus.PENDING, ActionStatus.ACCEPTED))

    def test_creation_rights(self):
        pending_init = SimpleNamespace(type=Action.INIT, status=ActionStatus.PENDING)

        root = find_edge(self.handler, Action.INIT, ActionStatus.PENDING)
        child = find_edge(self.handler, Action.VALORIZE, ActionStatus.CREATED, parent=pending_init)

        self.assertEqual(root, (None, (Action.INIT, ActionStatus.PENDING), can_create_consumption))
        self.assertIsNone(find_edge(self.handler, Action.INIT, ActionStatus.PENDING, parent=pending_init))
        self.assertIsNone(find_edge(self.handler, Action.VALORIZE, ActionStatus.CREATED))
        self.assertEqual(
            child,
            ((Action.INIT, ActionStatus.PENDING), (Action.VALORIZE, ActionStatus.CREATED), can_create_valorization),
        )
        self.assertIsNone(
            find_edge(
                self.handler,
                Action.VALORIZE,
                ActionStatus.CREATED,
                parent=SimpleNamespace(type=Action.INIT, status=ActionStatus.ACCEPTED),
            )
        )
        self.assertIsNone(
            find_edge(
                self.handler,
                Action.VALORIZE,
                ActionStatus.CREATED,
                parent=SimpleNamespace(type=Action.VALORIZE, status=ActionStatus.PENDING),
            )
        )
