from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from core.models import Entity
from traceability.handlers.action import ActionIndustryHandler
from traceability.models import Action, ActionStatus
from traceability.serializers.action_authorization import ActionAuthorizationSerializer


class GenericActionHandler(ActionIndustryHandler):
    industry = "TEST"
    action_creation_flow = (
        (None, (Action.INIT, ActionStatus.PENDING)),
        ((Action.INIT, ActionStatus.PENDING), (Action.VALORIZE, ActionStatus.CREATED)),
    )


class ActionAuthorizationSerializerTest(SimpleTestCase):
    def setUp(self):
        self.holder = Entity(id=1, entity_type=Entity.OPERATOR)
        self.parent = Action(id=3, type=Action.INIT, industry=GenericActionHandler.industry, holder=self.holder)
        self.parent.status = ActionStatus.PENDING

    def validate_action(self, data, parent=None, holder=None):
        serializer = ActionAuthorizationSerializer(
            data=data,
            context={"handler": GenericActionHandler()},
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

    def test_rejects_unknown_edge(self):
        unknown_edge = self.validate_action({"type": Action.VALORIZE, "status": ActionStatus.CREATED, "holder": 1})

        self.assertFalse(unknown_edge.is_valid())

    def test_rejects_parent_from_another_industry(self):
        self.parent.industry = "OTHER"
        serializer = self.validate_action(
            {"type": Action.VALORIZE, "status": ActionStatus.CREATED, "parent": 3, "holder": 1}
        )

        self.assertFalse(serializer.is_valid())

    def test_find_edge_matches_parent_type_and_status(self):
        handler = GenericActionHandler()
        find_edge = ActionAuthorizationSerializer.find_edge

        self.assertIsNotNone(find_edge(handler, Action.VALORIZE, ActionStatus.CREATED, self.parent))
        self.assertIsNone(find_edge(handler, "UNKNOWN", ActionStatus.CREATED, self.parent))
        self.assertIsNone(find_edge(handler, Action.VALORIZE, ActionStatus.PENDING, self.parent))
        self.parent.type = Action.VALORIZE
        self.assertIsNone(find_edge(handler, Action.VALORIZE, ActionStatus.CREATED, self.parent))
        self.parent.type = Action.INIT
        self.parent.status = ActionStatus.ACCEPTED
        self.assertIsNone(find_edge(handler, Action.VALORIZE, ActionStatus.CREATED, self.parent))

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
