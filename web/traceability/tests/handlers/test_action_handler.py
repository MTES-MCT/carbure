from decimal import Decimal

from django.test import TestCase

from h2.handlers import H2ActionHandler
from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.registry import get_action_handler
from traceability.models import Action


class ActionHandlerRegistryTest(TestCase):
    def test_returns_the_h2_handler_for_the_h2_industry(self):
        handler = get_action_handler(Action.H2)

        self.assertIsInstance(handler, H2ActionHandler)
        self.assertEqual(handler.industry, Action.H2)

    def test_raises_for_an_unknown_industry(self):
        with self.assertRaises(ValueError):
            get_action_handler("BIOMASS")


class ActionIndustryHandlerQuantityTest(TestCase):
    def test_default_handler_only_knows_mj(self):
        handler = ActionIndustryHandler()
        quantity = Decimal("120000.000")

        self.assertEqual(handler.units, ["MJ"])
        self.assertEqual(handler.excel_quantity_unit, "MJ")
        self.assertEqual(handler.to_mj(quantity, "MJ"), quantity)
        self.assertEqual(handler.from_mj(quantity, "MJ"), quantity)
