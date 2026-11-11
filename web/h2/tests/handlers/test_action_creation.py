from types import SimpleNamespace

from django.test import SimpleTestCase

from h2.handlers.action import H2ActionHandler
from traceability.models import Action, ActionStatus
from traceability.serializers.action_authorization import ActionAuthorizationSerializer

find_edge = ActionAuthorizationSerializer.find_edge


class H2ActionCreationTest(SimpleTestCase):
    def setUp(self):
        self.handler = H2ActionHandler()

    def test_creation_flow(self):
        pending_init = SimpleNamespace(type=Action.INIT, status=ActionStatus.PENDING)

        root = find_edge(self.handler, Action.INIT, ActionStatus.PENDING)
        child = find_edge(self.handler, Action.VALORIZE, ActionStatus.CREATED, parent=pending_init)

        self.assertEqual(root, (None, (Action.INIT, ActionStatus.PENDING)))
        self.assertIsNone(find_edge(self.handler, Action.INIT, ActionStatus.PENDING, parent=pending_init))
        self.assertIsNone(find_edge(self.handler, Action.VALORIZE, ActionStatus.CREATED))
        self.assertEqual(
            child,
            ((Action.INIT, ActionStatus.PENDING), (Action.VALORIZE, ActionStatus.CREATED)),
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
