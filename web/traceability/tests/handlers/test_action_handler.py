from django.test import TestCase

from traceability.factories import MaterialFactory
from traceability.handlers import ActionIndustryHandler, get_action_handler
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

    def test_default_handler_has_no_field_lookups(self):
        handler = ActionIndustryHandler()

        self.assertIsNone(handler.lookup("material"))
        self.assertIsNone(handler.lookup("site"))

    def test_h2_handler_looks_up_hydrogen_materials(self):
        hydrogen = MaterialFactory(code="H2-GASE", name="Hydrogène gazeux")
        MaterialFactory(code="BIO-WOOD", name="Bois")

        materials = list(get_action_handler(Action.H2).lookup("material"))

        self.assertEqual(materials, [hydrogen])
