"""Unit tests for WatchedFieldsActionMixin"""

from unittest.mock import Mock

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

from biomethane.views.mixins import WatchedFieldsActionMixin


class WatchedFieldsActionMixinTests(TestCase):
    """Tests for WatchedFieldsActionMixin"""

    def setUp(self):
        """Initial setup for tests"""
        self.factory = APIRequestFactory()
        self.request = self.factory.get("/fake-url/watched-fields")

        # Create a test ViewSet with the mixin
        class TestViewSet(WatchedFieldsActionMixin):
            def __init__(self):
                self.action = "watched_fields"

            def get_queryset(self):
                return self.queryset

            def filter_queryset(self, queryset):
                return queryset

        self.viewset = TestViewSet()

    def test_watched_fields_success(self):
        """Test that watched_fields returns watched fields when the object exists"""
        # Create a mock object with watched fields
        mock_instance = Mock()
        mock_instance.watched_fields = ["watched_field1", "watched_field2"]

        # Create a mock queryset that returns the instance
        mock_model = Mock()
        mock_queryset = Mock()
        mock_queryset.get.return_value = mock_instance
        mock_queryset.model = mock_model
        self.viewset.queryset = mock_queryset

        # Execute the action
        response = self.viewset.watched_fields(self.request)

        # Verify results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ["watched_field1", "watched_field2"])
        mock_queryset.get.assert_called_once()

    def test_watched_fields_not_found(self):
        """Test that watched_fields returns an empty list when the object does not exist"""
        # Create a mock queryset that raises DoesNotExist
        mock_model = Mock()
        mock_model.DoesNotExist = Exception

        mock_queryset = Mock()
        mock_queryset.get.side_effect = mock_model.DoesNotExist
        mock_queryset.model = mock_model
        self.viewset.queryset = mock_queryset

        # Execute the action
        response = self.viewset.watched_fields(self.request)

        # Verify results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        mock_queryset.get.assert_called_once()

    def test_watched_fields_empty_list(self):
        """Test that watched_fields can return an empty list even if the object exists"""
        # Create a mock object with an empty list of watched fields
        mock_instance = Mock()
        mock_instance.watched_fields = []

        mock_model = Mock()
        mock_queryset = Mock()
        mock_queryset.get.return_value = mock_instance
        mock_queryset.model = mock_model
        self.viewset.queryset = mock_queryset

        # Execute the action
        response = self.viewset.watched_fields(self.request)

        # Verify results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
