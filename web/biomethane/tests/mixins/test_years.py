"""Unit tests for YearsActionMixin"""

from unittest.mock import Mock

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

from biomethane.views.mixins import YearsActionMixin


class YearsActionMixinTests(TestCase):
    """Tests for YearsActionMixin"""

    def setUp(self):
        """Initial setup for tests"""
        self.factory = APIRequestFactory()
        self.request = self.factory.get("/fake-url/years")

        # Create a test ViewSet with the mixin
        class TestViewSet(YearsActionMixin):
            def __init__(self):
                self.action = "get_years"

            def get_queryset(self):
                return self.queryset

            def filter_queryset(self, queryset):
                return queryset

        self.viewset = TestViewSet()

    def test_get_years_success(self):
        """Test that get_years returns sorted years"""
        # Create a mock queryset that returns years
        mock_queryset = Mock()
        mock_values_list = Mock()
        mock_values_list.distinct.return_value = [2023, 2021, 2022, 2020, 2024]

        mock_queryset.values_list.return_value = mock_values_list
        self.viewset.queryset = mock_queryset

        # Execute the action
        response = self.viewset.get_years(self.request)

        # Verify results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [2020, 2021, 2022, 2023, 2024])
        mock_queryset.values_list.assert_called_once_with("year", flat=True)
        mock_values_list.distinct.assert_called_once()

    def test_get_years_empty_queryset(self):
        """Test that get_years returns an empty list when no years are present"""
        # Create a mock queryset that returns an empty list
        mock_queryset = Mock()
        mock_values_list = Mock()
        mock_values_list.distinct.return_value = []

        mock_queryset.values_list.return_value = mock_values_list
        self.viewset.queryset = mock_queryset

        # Execute the action
        response = self.viewset.get_years(self.request)

        # Verify results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_years_single_year(self):
        """Test that get_years works with a single year"""
        # Create a mock queryset that returns a single year
        mock_queryset = Mock()
        mock_values_list = Mock()
        mock_values_list.distinct.return_value = [2023]

        mock_queryset.values_list.return_value = mock_values_list
        self.viewset.queryset = mock_queryset

        # Execute the action
        response = self.viewset.get_years(self.request)

        # Verify results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [2023])

    def test_get_years_with_duplicates(self):
        """Test that get_years correctly handles duplicates (via distinct())"""
        # Create a mock queryset - distinct() should have already eliminated duplicates
        mock_queryset = Mock()
        mock_values_list = Mock()
        # distinct() already returns a list without duplicates
        mock_values_list.distinct.return_value = [2023, 2021, 2022]

        mock_queryset.values_list.return_value = mock_values_list
        self.viewset.queryset = mock_queryset

        # Execute the action
        response = self.viewset.get_years(self.request)

        # Verify results - years must be sorted
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [2021, 2022, 2023])
