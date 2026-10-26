from types import SimpleNamespace

from django.test import SimpleTestCase

from traceability.handlers.action import ActionIndustryHandler
from traceability.lifecycle.checks import can_change_status, can_create
from traceability.lifecycle.rules import Creation, Transition


class SampleHandler(ActionIndustryHandler):
    transitions = (Transition("A", "FROM", "TO"),)
    creations = (
        Creation("ROOT", "PENDING", root=True),
        Creation("CHILD", "CREATED", parent="ROOT", parent_status="PENDING"),
    )


class CanChangeStatusTest(SimpleTestCase):
    def test_returns_the_matching_transition(self):
        transition = can_change_status(SampleHandler(), "A", "FROM", "TO")

        self.assertEqual(transition.to_status, "TO")

    def test_returns_none_when_one_field_differs(self):
        handler = SampleHandler()

        self.assertIsNone(can_change_status(handler, "OTHER", "FROM", "TO"))
        self.assertIsNone(can_change_status(handler, "A", "OTHER", "TO"))
        self.assertIsNone(can_change_status(handler, "A", "FROM", "OTHER"))

    def test_returns_none_when_the_handler_has_no_transition(self):
        self.assertIsNone(can_change_status(ActionIndustryHandler(), "A", "FROM", "TO"))


class CanCreateTest(SimpleTestCase):
    def test_returns_a_root_creation_without_parent(self):
        creation = can_create(SampleHandler(), "ROOT")

        self.assertEqual(creation.action_type, "ROOT")
        self.assertEqual(creation.status, "PENDING")

    def test_returns_none_for_a_child_without_parent(self):
        self.assertIsNone(can_create(SampleHandler(), "CHILD"))

    def test_returns_a_child_creation_under_an_allowed_parent(self):
        parent = SimpleNamespace(type="ROOT", status="PENDING")

        creation = can_create(SampleHandler(), "CHILD", parent=parent)

        self.assertEqual(creation.action_type, "CHILD")
        self.assertEqual(creation.status, "CREATED")

    def test_returns_none_when_the_parent_type_or_status_is_not_allowed(self):
        handler = SampleHandler()

        self.assertIsNone(can_create(handler, "CHILD", parent=SimpleNamespace(type="OTHER", status="PENDING")))
        self.assertIsNone(can_create(handler, "CHILD", parent=SimpleNamespace(type="ROOT", status="OTHER")))
        self.assertIsNone(can_create(handler, "ROOT", parent=SimpleNamespace(type="ROOT", status="PENDING")))

    def test_returns_none_when_the_type_is_absent(self):
        self.assertIsNone(can_create(SampleHandler(), "MISSING"))
