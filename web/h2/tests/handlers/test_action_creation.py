from types import SimpleNamespace

from django.test import SimpleTestCase

from h2.handlers.action import H2ActionHandler
from traceability.models import Action, ActionStatus


class H2ActionCreationTest(SimpleTestCase):
    def setUp(self):
        self.handler = H2ActionHandler()

    def test_creation_flow(self):
        pending_init = SimpleNamespace(type=Action.INIT, status=ActionStatus.PENDING)

        self.assertTrue(self.handler.can_create_action(Action.INIT, ActionStatus.PENDING))
        self.assertTrue(self.handler.can_create_action(Action.VALORIZE, ActionStatus.CREATED, parent=pending_init))
        self.assertFalse(self.handler.can_create_action(Action.INIT, ActionStatus.PENDING, parent=pending_init))
        self.assertFalse(self.handler.can_create_action(Action.VALORIZE, ActionStatus.CREATED))
        self.assertFalse(
            self.handler.can_create_action(
                Action.VALORIZE,
                ActionStatus.CREATED,
                parent=SimpleNamespace(type=Action.INIT, status=ActionStatus.ACCEPTED),
            )
        )
        self.assertFalse(
            self.handler.can_create_action(
                Action.VALORIZE,
                ActionStatus.CREATED,
                parent=SimpleNamespace(type=Action.VALORIZE, status=ActionStatus.PENDING),
            )
        )
