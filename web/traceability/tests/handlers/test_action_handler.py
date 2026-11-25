from django.test import SimpleTestCase, TestCase

from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.registry import get_action_handler
from traceability.models import Action, Industry
from traceability.serializers.consumption import ConsumptionSerializer
from traceability.serializers.transfer import TransferSerializer


class GenericActionHandler(ActionIndustryHandler):
    industry = "TEST"


class ActionCreationSerializersTest(SimpleTestCase):
    def test_industry_inherits_default_serializer(self):
        self.assertIs(GenericActionHandler.get_action_creation_serializers()[Action.CONSUME], ConsumptionSerializer)

    def test_industry_can_extend_and_override_defaults(self):
        class IndustryHandler(ActionIndustryHandler):
            action_creation_serializers = {Action.VALORIZE: object}

        class OtherIndustryHandler(ActionIndustryHandler):
            action_creation_serializers = {Action.CONSUME: str}

        self.assertEqual(
            IndustryHandler.get_action_creation_serializers(),
            {Action.CONSUME: ConsumptionSerializer, Action.TRANSFER: TransferSerializer, Action.VALORIZE: object},
        )
        self.assertIs(OtherIndustryHandler.get_action_creation_serializers()[Action.CONSUME], str)
        self.assertEqual(
            ActionIndustryHandler.get_action_creation_serializers(),
            {Action.CONSUME: ConsumptionSerializer, Action.TRANSFER: TransferSerializer},
        )


class ActionHandlerRegistryTest(TestCase):
    def test_returns_the_h2_handler_for_the_h2_industry(self):
        from h2.handlers.action import H2ActionHandler

        handler = get_action_handler(Industry.H2)

        self.assertIsInstance(handler, H2ActionHandler)
        self.assertEqual(handler.industry, Industry.H2)

    def test_raises_for_an_unknown_industry(self):
        with self.assertRaises(ValueError):
            get_action_handler("BIOMASS")
