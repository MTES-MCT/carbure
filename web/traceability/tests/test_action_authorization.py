from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from core.models import Entity
from traceability.handlers.action import ActionIndustryHandler
from traceability.models import Action, ActionStatus
from traceability.serializers.action_authorization import ActionAuthorizationSerializer


def is_holder(actor, holder, parent_holder):
    return actor == holder


class GenericActionHandler(ActionIndustryHandler):
    industry = "TEST"
    action_creation_flow = (
        (None, (Action.INIT, ActionStatus.PENDING)),
        ((Action.INIT, ActionStatus.PENDING), (Action.VALORIZE, ActionStatus.CREATED)),
    )
    action_status_authorizations = {
        (Action.INIT, ActionStatus.PENDING): is_holder,
        (Action.VALORIZE, ActionStatus.CREATED): is_holder,
    }


class ActionAuthorizationSerializerTest(SimpleTestCase):
    def setUp(self):
        self.holder = Entity(id=1, entity_type=Entity.OPERATOR)
        self.parent = Action(id=3, type=Action.INIT, industry=GenericActionHandler.industry, holder=self.holder)
        self.parent.status = ActionStatus.PENDING

    def validate_action(self, data, parent=None, holder=None, actor=None):
        serializer = ActionAuthorizationSerializer(
            data=data,
            context={"handler": GenericActionHandler(), "entity": actor or self.holder},
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

    def test_validates_child_and_returns_resolved_values_and_status(self):
        serializer = self.validate_action(
            {"type": Action.VALORIZE, "status": ActionStatus.CREATED, "parent": 3, "holder": 1}
        )

        self.assertEqual(serializer.errors, {})
        self.assertIs(serializer.validated_data["parent"], self.parent)
        self.assertIs(serializer.validated_data["holder"], self.holder)
        self.assertEqual(serializer.validated_data["status"], ActionStatus.CREATED)

    def test_validates_root_without_parent(self):
        serializer = self.validate_action({"type": Action.INIT, "status": ActionStatus.PENDING, "holder": 1})

        self.assertEqual(serializer.errors, {})
        self.assertEqual(serializer.validated_data["status"], ActionStatus.PENDING)

    def test_authorization_receives_actor_holder_and_parent_holder_in_order(self):
        actor = Entity(id=2, entity_type=Entity.ADMIN)
        holder = Entity(id=4, entity_type=Entity.HRS)
        authorize = Mock(return_value=True)
        with patch.object(
            GenericActionHandler, "action_status_authorizations", {(Action.VALORIZE, ActionStatus.CREATED): authorize}
        ):
            serializer = self.validate_action(
                {"type": Action.VALORIZE, "status": ActionStatus.CREATED, "parent": 3, "holder": holder.id},
                holder=holder,
                actor=actor,
            )

        self.assertEqual(serializer.errors, {})
        authorize.assert_called_once_with(actor, holder, self.holder)

    def test_refuses_missing_or_denied_status_authorization(self):
        denied = Mock(return_value=False)
        for rules in ({}, {(Action.INIT, ActionStatus.PENDING): denied}):
            with self.subTest(rules=rules), patch.object(GenericActionHandler, "action_status_authorizations", rules):
                serializer = self.validate_action({"type": Action.INIT, "status": ActionStatus.PENDING, "holder": 1})

                self.assertIn("non_field_errors", serializer.errors)
        denied.assert_called_once_with(self.holder, self.holder, None)

    def test_rejects_unknown_edge(self):
        unknown_edge = self.validate_action({"type": Action.VALORIZE, "status": ActionStatus.CREATED, "holder": 1})

        self.assertFalse(unknown_edge.is_valid())

    def test_rejects_parent_from_another_industry(self):
        self.parent.industry = "OTHER"
        serializer = self.validate_action(
            {"type": Action.VALORIZE, "status": ActionStatus.CREATED, "parent": 3, "holder": 1}
        )

        self.assertFalse(serializer.is_valid())

    def test_can_create_action_matches_parent_type_and_status(self):
        handler = GenericActionHandler()

        self.assertIs(handler.can_create_action(Action.VALORIZE, ActionStatus.CREATED, self.parent), True)
        self.assertIs(handler.can_create_action("UNKNOWN", ActionStatus.CREATED, self.parent), False)
        self.assertIs(handler.can_create_action(Action.VALORIZE, ActionStatus.PENDING, self.parent), False)
        self.parent.type = Action.VALORIZE
        self.assertIs(handler.can_create_action(Action.VALORIZE, ActionStatus.CREATED, self.parent), False)
        self.parent.type = Action.INIT
        self.parent.status = ActionStatus.ACCEPTED
        self.assertIs(handler.can_create_action(Action.VALORIZE, ActionStatus.CREATED, self.parent), False)

    def test_rejects_missing_or_invalid_status(self):
        for fields in ({}, {"status": "UNKNOWN"}, {"status": None}, {"status": ""}):
            with self.subTest(fields=fields):
                serializer = self.validate_action({"type": Action.INIT, "holder": 1, **fields})

                self.assertIn("status", serializer.errors)

    def test_rejects_status_without_matching_edge(self):
        for data in (
            {"type": Action.INIT, "status": ActionStatus.CREATED, "holder": 1},
            {"type": Action.VALORIZE, "status": ActionStatus.PENDING, "parent": 3, "holder": 1},
        ):
            with self.subTest(data=data):
                serializer = self.validate_action(data)

                self.assertIn("non_field_errors", serializer.errors)
