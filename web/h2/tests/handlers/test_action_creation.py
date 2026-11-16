from types import SimpleNamespace

from django.test import SimpleTestCase

from core.models import Entity
from h2.handlers.action import H2ActionHandler
from traceability.models import Action, ActionStatus


class H2ActionCreationTest(SimpleTestCase):
    def setUp(self):
        self.handler = H2ActionHandler()

    def test_creation_flow(self):
        pending_init = SimpleNamespace(type=Action.INIT, status=ActionStatus.PENDING)
        created_valorize = SimpleNamespace(type=Action.VALORIZE, status=ActionStatus.CREATED)

        self.assertTrue(self.handler.can_create_action(Action.INIT, ActionStatus.PENDING))
        self.assertTrue(self.handler.can_create_action(Action.VALORIZE, ActionStatus.CREATED, parent=pending_init))
        self.assertTrue(self.handler.can_create_action(Action.TRANSFER, ActionStatus.PENDING, parent=created_valorize))
        self.assertFalse(self.handler.can_create_action(Action.INIT, ActionStatus.PENDING, parent=pending_init))
        self.assertFalse(self.handler.can_create_action(Action.VALORIZE, ActionStatus.CREATED))
        self.assertFalse(self.handler.can_create_action(Action.TRANSFER, ActionStatus.PENDING))
        self.assertFalse(self.handler.can_create_action(Action.TRANSFER, ActionStatus.CREATED, parent=created_valorize))
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
        self.assertFalse(
            self.handler.can_create_action(
                Action.TRANSFER,
                ActionStatus.PENDING,
                parent=SimpleNamespace(type=Action.VALORIZE, status=ActionStatus.PENDING),
            )
        )
        self.assertFalse(
            self.handler.can_create_action(
                Action.TRANSFER,
                ActionStatus.PENDING,
                parent=pending_init,
            )
        )

    def test_only_the_hrs_holding_the_certificate_can_create_a_transfer(self):
        hrs = Entity(id=1, entity_type=Entity.HRS)
        other_hrs = Entity(id=2, entity_type=Entity.HRS)
        recipient = Entity(id=3, entity_type=Entity.OPERATOR)
        certificate = SimpleNamespace(type=Action.VALORIZE, status=ActionStatus.CREATED, holder=hrs)

        self.assertTrue(self.handler.can_assign_status(hrs, Action.TRANSFER, ActionStatus.PENDING, recipient, certificate))
        self.assertFalse(
            self.handler.can_assign_status(other_hrs, Action.TRANSFER, ActionStatus.PENDING, recipient, certificate)
        )
        self.assertFalse(
            self.handler.can_assign_status(recipient, Action.TRANSFER, ActionStatus.PENDING, recipient, certificate)
        )
        self.assertFalse(self.handler.can_assign_status(hrs, Action.TRANSFER, ActionStatus.CREATED, recipient, certificate))
