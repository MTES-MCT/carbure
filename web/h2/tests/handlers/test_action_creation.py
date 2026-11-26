from types import SimpleNamespace

from django.test import SimpleTestCase

from core.models import Entity
from h2.handlers.action import H2ActionHandler
from traceability.models import Action, ActionStatus


class H2ActionCreationTest(SimpleTestCase):
    def setUp(self):
        self.handler = H2ActionHandler()

    def test_creation_flow(self):
        pending_consume = SimpleNamespace(type=Action.CONSUME, status=ActionStatus.PENDING)
        created_valorize = SimpleNamespace(type=Action.VALORIZE, status=ActionStatus.CREATED)

        self.assertTrue(self.handler.can_create_action(Action.CONSUME, ActionStatus.PENDING))
        self.assertTrue(self.handler.can_create_action(Action.VALORIZE, ActionStatus.CREATED, parent=pending_consume))
        self.assertTrue(self.handler.can_create_action(Action.TRANSFER, ActionStatus.PENDING, parent=created_valorize))
        self.assertFalse(self.handler.can_create_action(Action.CONSUME, ActionStatus.PENDING, parent=pending_consume))
        self.assertFalse(self.handler.can_create_action(Action.VALORIZE, ActionStatus.CREATED))
        self.assertFalse(self.handler.can_create_action(Action.TRANSFER, ActionStatus.PENDING))
        self.assertFalse(self.handler.can_create_action(Action.TRANSFER, ActionStatus.CREATED, parent=created_valorize))
        self.assertFalse(
            self.handler.can_create_action(
                Action.VALORIZE,
                ActionStatus.CREATED,
                parent=SimpleNamespace(type=Action.CONSUME, status=ActionStatus.ACCEPTED),
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
                parent=pending_consume,
            )
        )
        accepted_transfer = SimpleNamespace(type=Action.TRANSFER, status=ActionStatus.ACCEPTED)
        self.assertTrue(self.handler.can_create_action(Action.TRANSFER, ActionStatus.PENDING, parent=accepted_transfer))
        self.assertTrue(self.handler.can_create_action(Action.CONSUME, ActionStatus.CREATED, parent=accepted_transfer))
        self.assertFalse(self.handler.can_create_action(Action.CONSUME, ActionStatus.CREATED, parent=created_valorize))
        self.assertFalse(
            self.handler.can_create_action(
                Action.CONSUME,
                ActionStatus.CREATED,
                parent=SimpleNamespace(type=Action.TRANSFER, status=ActionStatus.PENDING),
            )
        )

    def test_only_the_hrs_holding_the_certificate_can_create_a_transfer(self):
        hrs = Entity(id=1, entity_type=Entity.HRS)
        other_hrs = Entity(id=2, entity_type=Entity.HRS)
        recipient = Entity(id=3, entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        other_operator = Entity(id=4, entity_type=Entity.OPERATOR, is_tiruert_liable=False)
        certificate = SimpleNamespace(type=Action.VALORIZE, status=ActionStatus.CREATED, holder=hrs)

        self.assertTrue(self.handler.can_assign_status(hrs, Action.TRANSFER, ActionStatus.PENDING, recipient, certificate))
        self.assertFalse(
            self.handler.can_assign_status(other_hrs, Action.TRANSFER, ActionStatus.PENDING, recipient, certificate)
        )
        self.assertFalse(
            self.handler.can_assign_status(recipient, Action.TRANSFER, ActionStatus.PENDING, recipient, certificate)
        )
        self.assertFalse(self.handler.can_assign_status(hrs, Action.TRANSFER, ActionStatus.CREATED, recipient, certificate))
        self.assertFalse(
            self.handler.can_assign_status(hrs, Action.TRANSFER, ActionStatus.PENDING, other_operator, certificate)
        )

    def test_the_liable_holding_an_accepted_transfer_can_cede_or_consume_it(self):
        liable = Entity(id=1, entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        recipient = Entity(id=2, entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        other = Entity(id=3, entity_type=Entity.OPERATOR, is_tiruert_liable=False)
        volume = SimpleNamespace(type=Action.TRANSFER, status=ActionStatus.ACCEPTED, holder=liable)

        self.assertTrue(self.handler.can_assign_status(liable, Action.TRANSFER, ActionStatus.PENDING, recipient, volume))
        self.assertTrue(self.handler.can_assign_status(liable, Action.CONSUME, ActionStatus.CREATED, liable, volume))
        self.assertFalse(self.handler.can_assign_status(liable, Action.TRANSFER, ActionStatus.PENDING, liable, volume))
        self.assertFalse(self.handler.can_assign_status(liable, Action.TRANSFER, ActionStatus.PENDING, other, volume))
        self.assertFalse(self.handler.can_assign_status(recipient, Action.CONSUME, ActionStatus.CREATED, liable, volume))
        self.assertFalse(self.handler.can_assign_status(liable, Action.CONSUME, ActionStatus.CREATED, recipient, volume))
