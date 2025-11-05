"""Unit tests for OptionalFieldsActionMixin"""

from unittest.mock import Mock

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

from biomethane.views.mixins import OptionalFieldsActionMixin


class OptionalFieldsActionMixinTests(TestCase):
    """Tests for OptionalFieldsActionMixin"""

    def setUp(self):
        """Initial setup for tests"""
        self.factory = APIRequestFactory()
        self.request = self.factory.get("/fake-url/optional-fields")

        # Create a test ViewSet with the mixin
        class TestViewSet(OptionalFieldsActionMixin):
            def __init__(self):
                self.action = "get_optional_fields"

            def get_queryset(self):
                return self.queryset

        self.viewset = TestViewSet()

    def test_get_optional_fields_success(self):
        """Test that get_optional_fields returns optional fields when the object exists"""
        # Create a mock object with optional fields
        mock_instance = Mock()
        mock_instance.optional_fields = ["field1", "field2", "field3"]

        # Create a mock queryset that returns the instance
        mock_queryset = Mock()
        mock_queryset.get.return_value = mock_instance
        self.viewset.queryset = mock_queryset

        # Execute the action
        response = self.viewset.get_optional_fields(self.request)

        # Verify results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ["field1", "field2", "field3"])
        mock_queryset.get.assert_called_once()

    def test_get_optional_fields_not_found(self):
        """Test that get_optional_fields returns 404 when the object does not exist"""
        # Create a mock queryset that raises DoesNotExist
        mock_model = Mock()
        mock_model.DoesNotExist = Exception

        mock_queryset = Mock()
        mock_queryset.get.side_effect = mock_model.DoesNotExist
        mock_queryset.model = mock_model
        self.viewset.queryset = mock_queryset

        # Execute the action
        response = self.viewset.get_optional_fields(self.request)

        # Verify results
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        mock_queryset.get.assert_called_once()

    def test_get_optional_fields_empty_list(self):
        """Test that get_optional_fields can return an empty list"""
        # Create a mock object with an empty list of optional fields
        mock_instance = Mock()
        mock_instance.optional_fields = []

        mock_queryset = Mock()
        mock_queryset.get.return_value = mock_instance
        self.viewset.queryset = mock_queryset

        # Execute the action
        response = self.viewset.get_optional_fields(self.request)

        # Verify results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
