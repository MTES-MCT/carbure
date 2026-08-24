from django.test import TestCase

from traceability.handlers import get_action_handler
from traceability.handlers.h2 import H2ActionHandler
from traceability.models import Action


class ActionHandlerRegistryTest(TestCase):
    def test_returns_the_h2_handler_for_the_h2_industry(self):
        handler = get_action_handler(Action.H2)

        self.assertIsInstance(handler, H2ActionHandler)
        self.assertEqual(handler.industry, Action.H2)

    def test_raises_for_an_unknown_industry(self):
        with self.assertRaises(ValueError):
            get_action_handler("BIOMASS")
