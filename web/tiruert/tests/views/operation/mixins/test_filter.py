from datetime import datetime
from unittest.mock import Mock

from django.test import RequestFactory, TestCase
from rest_framework.request import Request

from tiruert.views.operation.mixins.filter import FilterActionMixin


class DummyFilterView(FilterActionMixin):
    """Minimal view implementation for testing filter endpoints."""

    def __init__(self):
        self.request = None
        self.queryset = None
        self.filterset_class = Mock()

    def get_queryset(self):
        return self.queryset


class FilterEndpointTest(TestCase):
    """Unit tests for filters() endpoint."""

    def setUp(self):
        self.factory = RequestFactory()
        self.view = DummyFilterView()

    def _make_drf_request(self, path):
        """Create a DRF Request from a Django request."""
        django_request = self.factory.get(path)
        return Request(django_request)

    def _setup_mock_queryset(self, return_values):
        """Setup mock queryset with given return values."""
        mock_queryset = Mock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.values_list.return_value.distinct.return_value = return_values
        self.view.queryset = mock_queryset

        # Setup filterset mock
        mock_filterset = Mock()
        mock_filterset.qs = mock_queryset
        self.view.filterset_class.return_value = mock_filterset

        return mock_queryset

    def test_raises_exception_when_no_filter_specified(self):
        """Test filters raises exception when filter parameter is missing."""
        request = self._make_drf_request("/operations/filters/")
        self.view.request = request

        with self.assertRaises(Exception) as context:
            self.view.filters(request)

        self.assertEqual(str(context.exception), "No filter was specified")

    def test_raises_exception_for_invalid_filter(self):
        """Test filters raises exception for non-existent filter."""
        self._setup_mock_queryset([])
        request = self._make_drf_request("/operations/filters/?filter=invalid_filter")
        self.view.request = request

        with self.assertRaises(Exception) as context:
            self.view.filters(request)

        self.assertEqual(str(context.exception), "Filter 'invalid_filter' does not exist for operations")

    def test_supported_filters_mapping(self):
        """Test all supported filters map to correct columns."""
        expected_mappings = {
            "status": "status",
            "sector": "_sector",
            "customs_category": "customs_category",
            "biofuel": "biofuel__code",
            "operation": "_type",
            "from_to": "_entity",
            "depot": "_depot",
            "type": "_transaction",
            "period": "created_at",
        }

        for filter_name, expected_column in expected_mappings.items():
            with self.subTest(filter=filter_name):
                mock_queryset = self._setup_mock_queryset([])
                request = self._make_drf_request(f"/operations/filters/?filter={filter_name}")
                self.view.request = request

                self.view.filters(request)

                mock_queryset.values_list.assert_called_with(expected_column, flat=True)

    def test_returns_unique_non_null_values(self):
        """Test filters returns unique values and excludes None."""
        self._setup_mock_queryset(["value1", "value2", "value1", None])
        request = self._make_drf_request("/operations/filters/?filter=status")
        self.view.request = request

        response = self.view.filters(request)

        self.assertEqual(set(response.data), {"value1", "value2"})

    def test_period_filter_formats_dates_as_yyyymm(self):
        """Test period filter formats datetime values as YYYYMM strings."""
        self._setup_mock_queryset([datetime(2024, 1, 15), datetime(2024, 11, 20)])
        request = self._make_drf_request("/operations/filters/?filter=period")
        self.view.request = request

        response = self.view.filters(request)

        self.assertIn("202401", response.data)
        self.assertIn("202411", response.data)


class FilterBalanceEndpointTest(TestCase):
    """Unit tests for filters_balance() endpoint."""

    def setUp(self):
        self.factory = RequestFactory()
        self.view = DummyFilterView()

    def _make_drf_request(self, path):
        """Create a DRF Request from a Django request."""
        django_request = self.factory.get(path)
        return Request(django_request)

    def _setup_mock_queryset(self, return_values):
        """Setup mock queryset with given return values."""
        mock_queryset = Mock()
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.values_list.return_value.distinct.return_value = return_values
        self.view.queryset = mock_queryset

        # Setup filterset mock
        mock_filterset = Mock()
        mock_filterset.qs = mock_queryset
        self.view.filterset_class.return_value = mock_filterset

        return mock_queryset

    def test_raises_exception_when_no_filter_specified(self):
        """Test filters_balance raises exception when filter parameter is missing."""
        request = self._make_drf_request("/operations/balance/filters/")
        self.view.request = request

        with self.assertRaises(Exception) as context:
            self.view.filters_balance(request)

        self.assertEqual(str(context.exception), "No filter was specified")

    def test_raises_exception_for_invalid_filter(self):
        """Test filters_balance raises exception for non-existent filter."""
        self._setup_mock_queryset([])
        request = self._make_drf_request("/operations/balance/filters/?filter=invalid_filter")
        self.view.request = request

        with self.assertRaises(Exception) as context:
            self.view.filters_balance(request)

        self.assertEqual(str(context.exception), "Filter 'invalid_filter' does not exist for balances")

    def test_supported_filters_mapping(self):
        """Test all supported filters map to correct columns."""
        expected_mappings = {
            "sector": "sector",
            "customs_category": "customs_category",
            "biofuel": "biofuel__code",
            "depot": "depots",
        }

        for filter_name, expected_column in expected_mappings.items():
            with self.subTest(filter=filter_name):
                mock_queryset = self._setup_mock_queryset([])
                request = self._make_drf_request(f"/operations/balance/filters/?filter={filter_name}")
                self.view.request = request

                self.view.filters_balance(request)

                mock_queryset.values_list.assert_called_with(expected_column, flat=True)

    def test_returns_unique_non_null_values(self):
        """Test filters_balance returns unique values and excludes None."""
        self._setup_mock_queryset(["value1", "value2", "value1", None])
        request = self._make_drf_request("/operations/balance/filters/?filter=biofuel")
        self.view.request = request

        response = self.view.filters_balance(request)

        self.assertEqual(set(response.data), {"value1", "value2"})
