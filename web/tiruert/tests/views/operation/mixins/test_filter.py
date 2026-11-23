from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase
from rest_framework.request import Request

from core.models import Biocarburant, Entity, MatierePremiere
from tiruert.models import Operation, OperationDetail
from tiruert.views.operation.mixins.filter import FilterActionMixin
from transactions.factories import CarbureLotFactory
from transactions.models import Depot


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
        # filters_balance instantiates OperationFilterForBalance directly, so patch it here
        # once for every test in this class instead of the unused self.view.filterset_class.
        self.mock_filterset_class = self.enterContext(
            patch("tiruert.views.operation.mixins.filter.OperationFilterForBalance")
        )

    def _make_drf_request(self, path):
        """Create a DRF Request from a Django request."""
        django_request = self.factory.get(path)
        return Request(django_request)

    def _setup_mock_queryset(self, return_values):
        """Setup mock queryset with given return values."""
        mock_operation_qs = Mock()
        self.view.queryset = mock_operation_qs
        self.mock_filterset_class.return_value.qs = mock_operation_qs

        # Setup OperationDetail mock queryset
        mock_details_qs = Mock()
        mock_details_qs.filter.return_value = mock_details_qs
        mock_details_qs.annotate.return_value = mock_details_qs
        mock_details_qs.values_list.return_value.distinct.return_value = return_values
        self._mock_details_qs = mock_details_qs

        return mock_details_qs

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

    @patch("tiruert.views.operation.mixins.filter.OperationDetail.objects")
    def test_supported_filters_mapping(self, mock_od_manager):
        """Test all supported filters map to correct columns."""
        expected_mappings = {
            "sector": "sector",
            "customs_category": "operation__customs_category",
            "biofuel": "operation__biofuel__code",
            "depot": "depots",
            "feedstock": "lot__feedstock__code",
            "durability_period": "operation__durability_period",
            "origin_country": "lot__country_of_origin__code_pays",
        }

        for filter_name, expected_column in expected_mappings.items():
            with self.subTest(filter=filter_name):
                mock_queryset = self._setup_mock_queryset([])
                mock_od_manager.filter.return_value = mock_queryset
                request = self._make_drf_request(f"/operations/balance/filters/?filter={filter_name}")
                self.view.request = request

                self.view.filters_balance(request)

                mock_queryset.values_list.assert_called_with(expected_column, flat=True)

    @patch("tiruert.views.operation.mixins.filter.OperationDetail.objects")
    def test_returns_unique_non_null_values(self, mock_od_manager):
        """Test filters_balance returns unique values and excludes None."""
        mock_details_qs = self._setup_mock_queryset(["value1", "value2", "value1", None])
        mock_od_manager.filter.return_value = mock_details_qs
        request = self._make_drf_request("/operations/balance/filters/?filter=biofuel")
        self.view.request = request

        response = self.view.filters_balance(request)

        self.assertEqual(set(response.data), {"value1", "value2"})


class FilterBalanceSectorAnnotationTest(TestCase):
    """Tests for sector annotations used by balance filters."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.view = DummyFilterView()

    def test_balance_sector_filter_returns_gpl_for_gpl_compatible_biofuel(self):
        """The balance sector annotation should include GPL."""
        entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        feedstock = MatierePremiere.biofuel.filter(category=MatierePremiere.CONV).first()
        biofuel = Biocarburant.objects.create(
            code="GPLF",
            name="Test GPL",
            name_en="Test GPL",
            description="Test GPL",
            compatible_essence=False,
            compatible_diesel=False,
            compatible_gpl=True,
        )
        operation = Operation.objects.create(
            type=Operation.INCORPORATION,
            status=Operation.VALIDATED,
            customs_category=MatierePremiere.CONV,
            biofuel=biofuel,
            credited_entity=entity,
            to_depot=Depot.objects.first(),
        )
        lot = CarbureLotFactory.create(
            carbure_client=entity,
            carbure_supplier=entity,
            carbure_producer=entity,
            feedstock=feedstock,
            biofuel=biofuel,
            lot_status="ACCEPTED",
            delivery_type="BLENDING",
            carbure_delivery_site=Depot.objects.first(),
        )
        OperationDetail.objects.create(operation=operation, lot=lot, volume=100, emission_rate_per_mj=10)

        queryset = Operation.objects.filter(id=operation.id)
        self.view.queryset = queryset
        self.view.filterset_class = lambda *args, **kwargs: SimpleNamespace(qs=queryset)
        request = Request(self.factory.get("/operations/balance/filters/?filter=sector"))
        self.view.request = request

        response = self.view.filters_balance(request)

        self.assertEqual(response.data, [Operation.GPL])
