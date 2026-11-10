from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from core.models import Entity
from h2.handlers.action import H2ActionHandler
from traceability.models import Action, ActionStatus
from traceability.serializers.action_authorization import ActionAuthorizationSerializer


class ActionAuthorizationSerializerTest(SimpleTestCase):
    def setUp(self):
        self.holder = Entity(id=1, entity_type=Entity.HRS)
        self.admin = Entity(id=2, entity_type=Entity.ADMIN)
        self.parent = Action(id=3, type=Action.INIT, industry=Action.H2, holder=self.holder)
        self.parent.status = ActionStatus.PENDING

    def validate_action(self, data, actor=None, parent=None, holder=None, handler=None):
        serializer = ActionAuthorizationSerializer(
            data=data,
            context={"entity": actor or self.admin, "handler": handler or H2ActionHandler()},
        )
        holder_queryset = Mock()
        holder_queryset.get.return_value = holder or self.holder
        parent_queryset = Mock()
        parent_queryset.get.return_value = parent or self.parent
        with (
            patch.object(serializer.fields["holder"], "get_queryset", return_value=holder_queryset),
            patch.object(serializer.fields["parent"], "get_queryset", return_value=parent_queryset),
        ):
            serializer.is_valid()
        return serializer

    def test_authorizes_child_and_returns_resolved_values_and_initial_status(self):
        serializer = self.validate_action({"type": Action.VALORIZE, "parent": 3, "holder": 1})

        self.assertEqual(serializer.errors, {})
        self.assertIs(serializer.validated_data["parent"], self.parent)
        self.assertIs(serializer.validated_data["holder"], self.holder)
        self.assertEqual(serializer.validated_data["initial_status"], ActionStatus.CREATED)

    def test_authorizes_root_without_parent(self):
        serializer = self.validate_action({"type": Action.INIT, "holder": 1}, actor=self.holder)

        self.assertEqual(serializer.errors, {})
        self.assertEqual(serializer.validated_data["initial_status"], ActionStatus.PENDING)

    def test_rejects_unauthorized_actor_and_unknown_edge(self):
        unauthorized = self.validate_action({"type": Action.VALORIZE, "parent": 3, "holder": 1}, actor=self.holder)
        unknown_edge = self.validate_action({"type": Action.VALORIZE, "holder": 1})

        self.assertFalse(unauthorized.is_valid())
        self.assertFalse(unknown_edge.is_valid())

    def test_rejects_parent_from_another_industry(self):
        self.parent.industry = "OTHER"
        serializer = self.validate_action({"type": Action.VALORIZE, "parent": 3, "holder": 1})

        self.assertFalse(serializer.is_valid())

    def test_rejects_edge_without_authorization_rule(self):
        handler = SimpleNamespace(
            industry=Action.H2, action_creation_flow=((None, (Action.INIT, ActionStatus.PENDING), None),)
        )
        serializer = self.validate_action({"type": Action.INIT, "holder": 1}, handler=handler)

        self.assertFalse(serializer.is_valid())

    def test_find_edge_matches_parent_type_and_status(self):
        handler = H2ActionHandler()
        find_edge = ActionAuthorizationSerializer.find_edge

        self.assertIsNotNone(find_edge(handler, Action.VALORIZE, self.parent))
        self.assertIsNone(find_edge(handler, "UNKNOWN", self.parent))
        self.parent.type = Action.VALORIZE
        self.assertIsNone(find_edge(handler, Action.VALORIZE, self.parent))
        self.parent.type = Action.INIT
        self.parent.status = ActionStatus.ACCEPTED
        self.assertIsNone(find_edge(handler, Action.VALORIZE, self.parent))
