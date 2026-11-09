from django.test import SimpleTestCase, TestCase

from h2.handlers import H2ActionHandler
from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.registry import get_action_handler
from traceability.models import Action
from traceability.serializers.consumption import ConsumptionSerializer


class ActionCreationSerializersTest(SimpleTestCase):
    def test_industry_inherits_default_serializer(self):
        self.assertIs(H2ActionHandler.get_action_creation_serializers()[Action.INIT], ConsumptionSerializer)

    def test_industry_can_extend_and_override_defaults(self):
        class IndustryHandler(ActionIndustryHandler):
            action_creation_serializers = {Action.VALORIZE: object}

        class OtherIndustryHandler(ActionIndustryHandler):
            action_creation_serializers = {Action.INIT: str}

        self.assertEqual(
            IndustryHandler.get_action_creation_serializers(),
            {Action.INIT: ConsumptionSerializer, Action.VALORIZE: object},
        )
        self.assertIs(OtherIndustryHandler.get_action_creation_serializers()[Action.INIT], str)
        self.assertEqual(ActionIndustryHandler.get_action_creation_serializers(), {Action.INIT: ConsumptionSerializer})


class ActionHandlerRegistryTest(TestCase):
    def test_returns_the_h2_handler_for_the_h2_industry(self):
        handler = get_action_handler(Action.H2)

        self.assertIsInstance(handler, H2ActionHandler)
        self.assertEqual(handler.industry, Action.H2)

    def test_raises_for_an_unknown_industry(self):
        with self.assertRaises(ValueError):
            get_action_handler("BIOMASS")
