from datetime import datetime
from unittest.mock import Mock

from django.test import RequestFactory, TestCase
from rest_framework.request import Request

from tiruert.views.elec_operation.mixins.filter import FilterActionMixin


class DummyFilterView(FilterActionMixin):
    """Minimal view implementation for testing filter endpoint."""

    def __init__(self):
        self.request = None
        self.queryset = None
        self.filterset_class = Mock()

    def get_queryset(self):
        return self.queryset


class ElecFilterActionMixinTest(TestCase):
    """Unit tests for filters() endpoint on electricity operations."""

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

        mock_filterset = Mock()
        mock_filterset.qs = mock_queryset
        self.view.filterset_class.return_value = mock_filterset

        return mock_queryset

    def test_raises_exception_when_no_filter_specified(self):
        """filters should raise when filter parameter is missing."""
        request = self._make_drf_request("/elec-operations/filters/")
        self.view.request = request

        with self.assertRaises(Exception) as context:
            self.view.filters(request)

        self.assertEqual(str(context.exception), "No filter was specified")

    def test_raises_exception_for_invalid_filter(self):
        """filters should raise for unsupported filter names."""
        self._setup_mock_queryset([])
        request = self._make_drf_request("/elec-operations/filters/?filter=unknown")
        self.view.request = request

        with self.assertRaises(Exception) as context:
            self.view.filters(request)

        self.assertEqual(str(context.exception), "Filter 'unknown' does not exist for operations")

    def test_supported_filters_mapping(self):
        """Supported filters should map to expected columns."""
        expected_mappings = {
            "status": "status",
            "operation": "_operation",
            "from_to": "_entity",
            "type": "_type",
            "period": "_period",
            "created_at": "created_at",
        }

        for filter_name, expected_column in expected_mappings.items():
            with self.subTest(filter=filter_name):
                mock_queryset = self._setup_mock_queryset([])
                request = self._make_drf_request(f"/elec-operations/filters/?filter={filter_name}")
                self.view.request = request

                self.view.filters(request)

                mock_queryset.values_list.assert_called_with(expected_column, flat=True)

    def test_returns_unique_non_null_values(self):
        """filters should return unique values and drop None."""
        self._setup_mock_queryset(["op1", "op2", "op1", None])
        request = self._make_drf_request("/elec-operations/filters/?filter=status")
        self.view.request = request

        response = self.view.filters(request)

        self.assertEqual(set(response.data), {"op1", "op2"})

    def test_created_at_filter_formats_dates(self):
        """created_at filter should format datetimes as YYYYMM strings."""
        self._setup_mock_queryset([datetime(2024, 1, 15), datetime(2024, 10, 5)])
        request = self._make_drf_request("/elec-operations/filters/?filter=created_at")
        self.view.request = request

        response = self.view.filters(request)

        self.assertIn("202401", response.data)
        self.assertIn("202410", response.data)
