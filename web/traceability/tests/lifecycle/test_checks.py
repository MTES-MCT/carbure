from django.test import SimpleTestCase

from traceability.handlers.action import ActionIndustryHandler
from traceability.lifecycle.checks import can_change_status
from traceability.lifecycle.rules import Transition


class SampleHandler(ActionIndustryHandler):
    transitions = (Transition("A", "FROM", "TO"),)


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
