from unittest.mock import Mock

from django.test import RequestFactory, TestCase

from core.models import Entity
from tiruert.views.mixins import UnitMixin


class BaseView:
    """Base view that provides minimal DRF-like interface."""

    def initialize_request(self, request, *args, **kwargs):
        """Base implementation that just returns the request."""
        return request

    def get_serializer_context(self):
        """Base implementation that returns minimal context."""
        return {"request": self.request, "format": None, "view": self}


class DummyViewWithUnitMixin(UnitMixin, BaseView):
    """Dummy view for testing UnitMixin."""

    pass


class UnitMixinTest(TestCase):
    """Tests for the UnitMixin."""

    def setUp(self):
        self.factory = RequestFactory()
        self.view = DummyViewWithUnitMixin()

    def test_initialize_request_with_get_parameter(self):
        """Unit should be extracted from GET parameter."""
        request = self.factory.get("/test/?unit=MJ")
        request.entity = None

        request = self.view.initialize_request(request)

        self.assertEqual(request.unit, "mj")

    def test_initialize_request_with_post_parameter(self):
        """Unit should be extracted from POST parameter."""
        request = self.factory.post("/test/", {"unit": "KG"})
        request.entity = None

        request = self.view.initialize_request(request)

        self.assertEqual(request.unit, "kg")

    def test_initialize_request_post_priority_over_get(self):
        """POST parameter should have priority over GET."""
        request = self.factory.post("/test/?unit=MJ", {"unit": "KG"})
        request.entity = None

        request = self.view.initialize_request(request)

        self.assertEqual(request.unit, "kg")

    def test_initialize_request_with_entity_preference(self):
        """Unit should be extracted from entity preference."""
        entity = Mock(spec=Entity)
        entity.preferred_unit = "MJ"

        request = self.factory.get("/test/")
        request.entity = entity

        request = self.view.initialize_request(request)

        self.assertEqual(request.unit, "mj")

    def test_initialize_request_parameter_over_entity_preference(self):
        """Request parameter should have priority over entity preference."""
        entity = Mock(spec=Entity)
        entity.preferred_unit = "MJ"

        request = self.factory.get("/test/?unit=KG")
        request.entity = entity

        request = self.view.initialize_request(request)

        self.assertEqual(request.unit, "kg")

    def test_initialize_request_default_to_liters(self):
        """Unit should default to 'l'."""
        request = self.factory.get("/test/")
        request.entity = None

        request = self.view.initialize_request(request)

        self.assertEqual(request.unit, "l")

    def test_initialize_request_lowercase_conversion(self):
        """Unit should be converted to lowercase."""
        request = self.factory.get("/test/?unit=MJ")
        request.entity = None

        request = self.view.initialize_request(request)

        self.assertEqual(request.unit, "mj")

    def test_get_serializer_context_with_unit(self):
        """Context should contain entity_id and unit."""
        entity = Mock(spec=Entity)
        entity.id = 123
        entity.preferred_unit = "l"

        request = self.factory.get("/test/?unit=MJ")
        request.entity = entity
        request = self.view.initialize_request(request)

        self.view.request = request
        context = self.view.get_serializer_context()

        self.assertEqual(context["entity_id"], 123)
        self.assertEqual(context["unit"], "mj")
