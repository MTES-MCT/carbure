from unittest.mock import Mock, patch

from django.test import SimpleTestCase, TestCase

from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.registry import get_action_handler
from traceability.models import Action, ActionStatus
from traceability.serializers.consumption import ConsumptionSerializer


class GenericActionHandler(ActionIndustryHandler):
    industry = "TEST"


class ActionCreationSerializersTest(SimpleTestCase):
    def test_industry_inherits_default_serializer(self):
        self.assertIs(GenericActionHandler.get_action_creation_serializers()[Action.INIT], ConsumptionSerializer)

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


class ActionStatusAuthorizationsTest(SimpleTestCase):
    def test_industry_extends_and_overrides_defaults_per_status(self):
        default = Mock()
        specific = Mock()
        defaults = {
            Action.INIT: {(ActionStatus.PENDING, ActionStatus.ACCEPTED): default},
            Action.VALORIZE: {(ActionStatus.CREATED,): default},
        }

        class IndustryHandler(ActionIndustryHandler):
            action_status_authorizations = {
                Action.INIT: {(ActionStatus.PENDING, ActionStatus.REJECTED): specific},
            }

        with patch.object(ActionIndustryHandler, "action_status_authorizations", defaults):
            self.assertEqual(
                IndustryHandler.get_action_status_authorizations(),
                {
                    Action.INIT: {
                        ActionStatus.PENDING: specific,
                        ActionStatus.ACCEPTED: default,
                        ActionStatus.REJECTED: specific,
                    },
                    Action.VALORIZE: {ActionStatus.CREATED: default},
                },
            )
            self.assertEqual(
                GenericActionHandler.get_action_status_authorizations(),
                {
                    Action.INIT: {ActionStatus.PENDING: default, ActionStatus.ACCEPTED: default},
                    Action.VALORIZE: {ActionStatus.CREATED: default},
                },
            )

        self.assertEqual(defaults[Action.INIT], {(ActionStatus.PENDING, ActionStatus.ACCEPTED): default})


class ActionHandlerRegistryTest(TestCase):
    def test_returns_the_h2_handler_for_the_h2_industry(self):
        from h2.handlers.action import H2ActionHandler

        handler = get_action_handler(Action.H2)

        self.assertIsInstance(handler, H2ActionHandler)
        self.assertEqual(handler.industry, Action.H2)

    def test_raises_for_an_unknown_industry(self):
        with self.assertRaises(ValueError):
            get_action_handler("BIOMASS")
