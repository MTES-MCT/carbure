from django.test import SimpleTestCase
from rest_framework.permissions import BasePermission

from traceability.handlers.action import ActionIndustryHandler
from traceability.lifecycle.checks import can_change_status, can_create
from traceability.lifecycle.rules import Creation, Transition


class Allow(BasePermission):
    def has_permission(self, request, view):
        return True


class SampleHandler(ActionIndustryHandler):
    transitions = (Transition("A", "FROM", "TO", Allow),)
    creations = (
        Creation("ROOT", root=True),
        Creation("CHILD", root=False, parents=("ROOT",)),
    )


class CanChangeStatusTest(SimpleTestCase):
    def test_returns_the_matching_transition(self):
        transition = can_change_status(SampleHandler(), "A", "FROM", "TO")

        self.assertEqual(transition.permission, Allow)

    def test_returns_none_when_one_field_differs(self):
        handler = SampleHandler()

        self.assertIsNone(can_change_status(handler, "OTHER", "FROM", "TO"))
        self.assertIsNone(can_change_status(handler, "A", "OTHER", "TO"))
        self.assertIsNone(can_change_status(handler, "A", "FROM", "OTHER"))

    def test_returns_none_when_the_handler_has_no_transition(self):
        self.assertIsNone(can_change_status(ActionIndustryHandler(), "A", "FROM", "TO"))


class CanCreateTest(SimpleTestCase):
    def test_returns_a_root_creation_without_parent(self):
        self.assertEqual(can_create(SampleHandler(), "ROOT").action_type, "ROOT")

    def test_returns_none_for_a_child_without_parent(self):
        self.assertIsNone(can_create(SampleHandler(), "CHILD"))

    def test_returns_a_child_creation_under_an_allowed_parent(self):
        self.assertEqual(can_create(SampleHandler(), "CHILD", parent_type="ROOT").action_type, "CHILD")

    def test_returns_none_when_the_parent_is_not_allowed(self):
        handler = SampleHandler()

        self.assertIsNone(can_create(handler, "CHILD", parent_type="OTHER"))
        self.assertIsNone(can_create(handler, "ROOT", parent_type="ROOT"))

    def test_returns_none_when_the_type_is_absent(self):
        self.assertIsNone(can_create(SampleHandler(), "MISSING"))
