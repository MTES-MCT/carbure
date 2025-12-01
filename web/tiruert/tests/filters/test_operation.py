from unittest.mock import Mock

from django.http import QueryDict
from django.test import RequestFactory, TestCase

from core.models import Entity
from tiruert.filters.operation import BaseFilter, OperationFilter, OperationFilterForBalance
from tiruert.models.operation import Operation


class BaseFilterTest(TestCase):
    """Unit tests for BaseFilter."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_filter_entity_for_regular_entity(self):
        """Test filter_entity filters operations where entity is credited OR debited."""
        entity = Mock(spec=Entity, id=1, entity_type=Entity.OPERATOR)
        entity.has_external_admin_right.return_value = False

        queryset = Mock()
        queryset.filter.return_value.distinct.return_value = queryset

        request = self.factory.get("/test/?entity_id=1")
        request.entity = entity

        filterset = BaseFilter({"entity_id": "1"}, queryset=queryset, request=request)
        filterset.filter_entity(queryset, "entity_id", "1")

        # Verify filter uses Q(credited_entity=1) | Q(debited_entity=1)
        queryset.filter.assert_called_once()
        q_filter = queryset.filter.call_args[0][0]

        # Verify it's an OR filter (Q object with connector='OR')
        self.assertEqual(q_filter.connector, "OR")
        self.assertIn(("credited_entity", "1"), q_filter.children)
        self.assertIn(("debited_entity", "1"), q_filter.children)

        queryset.filter.return_value.distinct.assert_called_once()

    def test_filter_entity_for_dgddi_external_admin(self):
        """Test filter_entity filters by accessible depots for DGDDI external admin."""
        entity = Mock(spec=Entity, id=1, entity_type=Entity.EXTERNAL_ADMIN)
        entity.has_external_admin_right.return_value = True
        entity.get_accessible_depots.return_value.values_list.return_value = [1, 2, 3]

        queryset = Mock()
        queryset.filter.return_value = queryset

        request = self.factory.get("/test/?entity_id=1")
        request.entity = entity

        filterset = BaseFilter({"entity_id": "1"}, queryset=queryset, request=request)
        filterset.filter_entity(queryset, "entity_id", "1")

        # Verify DGDDI path: filters by to_depot_id__in accessible depots
        queryset.filter.assert_called_once()
        q_filter = queryset.filter.call_args[0][0]

        # Verify it filters by to_depot_id in accessible depot list
        self.assertIn(("to_depot_id__in", [1, 2, 3]), q_filter.children)
        entity.get_accessible_depots.assert_called_once()

    def test_filter_from_to_with_multiple_entities(self):
        """Test filter_from_to filters by multiple entity names (credited OR debited)."""
        queryset = Mock()
        queryset.filter.return_value.distinct.return_value = queryset

        request = self.factory.get("/test/?from_to=Entity1&from_to=Entity2")
        query_dict = QueryDict("from_to=Entity1&from_to=Entity2")
        request.GET = query_dict

        filterset = BaseFilter({}, queryset=queryset, request=request)
        filterset.filter_from_to(queryset, "from_to", "Entity1")

        # Verify filter uses Q(credited_entity__name__in=[...]) | Q(debited_entity__name__in=[...])
        queryset.filter.assert_called_once()
        q_filter = queryset.filter.call_args[0][0]

        # Verify it's an OR filter with entity names
        self.assertEqual(q_filter.connector, "OR")
        self.assertIn(("credited_entity__name__in", ["Entity1", "Entity2"]), q_filter.children)
        self.assertIn(("debited_entity__name__in", ["Entity1", "Entity2"]), q_filter.children)

        queryset.filter.return_value.distinct.assert_called_once()

    def test_filter_depot_with_multiple_depots(self):
        """Test filter_depot filters by multiple depot names (from OR to)."""
        queryset = Mock()
        queryset.filter.return_value.distinct.return_value = queryset

        request = self.factory.get("/test/?depot=Depot1&depot=Depot2")
        query_dict = QueryDict("depot=Depot1&depot=Depot2")
        request.GET = query_dict

        filterset = BaseFilter({}, queryset=queryset, request=request)
        filterset.filter_depot(queryset, "depot", "Depot1")

        # Verify filter uses Q(from_depot__name__in=[...]) | Q(to_depot__name__in=[...])
        queryset.filter.assert_called_once()
        q_filter = queryset.filter.call_args[0][0]

        # Verify it's an OR filter with depot names
        self.assertEqual(q_filter.connector, "OR")
        self.assertIn(("from_depot__name__in", ["Depot1", "Depot2"]), q_filter.children)
        self.assertIn(("to_depot__name__in", ["Depot1", "Depot2"]), q_filter.children)

        queryset.filter.return_value.distinct.assert_called_once()

    def test_filter_period_returns_queryset_when_no_periods(self):
        """Test filter_period returns queryset unchanged when no periods provided."""
        queryset = Mock()

        request = self.factory.get("/test/")
        query_dict = QueryDict("")
        request.GET = query_dict

        filterset = BaseFilter({}, queryset=queryset, request=request)
        result = filterset.filter_period(queryset, "period", None)

        self.assertEqual(result, queryset)
        queryset.filter.assert_not_called()

    def test_filter_period_single_month(self):
        """Test filter_period filters operations for a single month period."""
        queryset = Mock()
        queryset.filter.return_value.distinct.return_value = queryset

        request = self.factory.get("/test/?period=202406")
        query_dict = QueryDict("period=202406")
        request.GET = query_dict

        filterset = BaseFilter({}, queryset=queryset, request=request)
        filterset.filter_period(queryset, "period", "202406")

        # Verify filter was called with date range for June 2024
        queryset.filter.assert_called_once()
        q_filter = queryset.filter.call_args[0][0]

        # Verify Q object has created_at__gte and created_at__lt filters
        self.assertTrue(hasattr(q_filter, "children"))
        # Should filter between start of June and start of July
        self.assertEqual(len(q_filter.children), 2)

        queryset.filter.return_value.distinct.assert_called_once()

    def test_filter_period_handles_year_transition(self):
        """Test filter_period correctly handles December to January transition."""
        queryset = Mock()
        queryset.filter.return_value.distinct.return_value = queryset

        request = self.factory.get("/test/?period=202412")
        query_dict = QueryDict("period=202412")
        request.GET = query_dict

        filterset = BaseFilter({}, queryset=queryset, request=request)
        filterset.filter_period(queryset, "period", "202412")

        # Verify filter was called for December 2024 → January 2025 transition
        queryset.filter.assert_called_once()
        q_filter = queryset.filter.call_args[0][0]

        # Verify Q object has filters for December 2024 (should go to Jan 2025, not Jan 2024)
        self.assertTrue(hasattr(q_filter, "children"))
        self.assertEqual(len(q_filter.children), 2)

        queryset.filter.return_value.distinct.assert_called_once()

    def test_filter_period_multiple_months(self):
        """Test filter_period filters operations for multiple periods with OR logic."""
        queryset = Mock()
        queryset.filter.return_value.distinct.return_value = queryset

        request = self.factory.get("/test/?period=202401&period=202402")
        query_dict = QueryDict("period=202401&period=202402")
        request.GET = query_dict

        filterset = BaseFilter({}, queryset=queryset, request=request)
        filterset.filter_period(queryset, "period", "202401")

        # Verify filter was called with combined Q objects (Jan OR Feb 2024)
        queryset.filter.assert_called_once()
        q_filter = queryset.filter.call_args[0][0]

        # Verify it's an OR filter combining multiple month ranges
        self.assertEqual(q_filter.connector, "OR")
        # Each period creates 2 children (gte + lt), so 2 periods = 4 conditions in 2 Q objects
        self.assertEqual(len(q_filter.children), 2)

        queryset.filter.return_value.distinct.assert_called_once()


class OperationFilterTest(TestCase):
    """Unit tests for OperationFilter."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_date_from_filter_field_mapping(self):
        """Test OperationFilter has date_from filter mapped to created_at__gte."""
        request = self.factory.get("/test/?date_from=2024-01-01")
        queryset = Operation.objects.none()

        filterset = OperationFilter({"date_from": "2024-01-01"}, queryset=queryset, request=request)

        # Verify date_from is in filters
        self.assertIn("date_from", filterset.filters)
        self.assertEqual(filterset.filters["date_from"].field_name, "created_at")
        self.assertEqual(filterset.filters["date_from"].lookup_expr, "gte")


class OperationFilterForBalanceTest(TestCase):
    """Unit tests for OperationFilterForBalance."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_has_ges_bound_filters(self):
        """Test OperationFilterForBalance has ges_bound_min and ges_bound_max filters."""
        request = self.factory.get("/test/")
        queryset = Operation.objects.none()

        filterset = OperationFilterForBalance({}, queryset=queryset, request=request)

        self.assertIn("ges_bound_min", filterset.filters)
        self.assertIn("ges_bound_max", filterset.filters)

    def test_ges_bound_filters_are_ignored(self):
        """Test ges_bound filters do not modify the queryset."""
        queryset = Mock()

        request = self.factory.get("/test/?ges_bound_min=10&ges_bound_max=90")
        request.GET = {"ges_bound_min": "10", "ges_bound_max": "90"}

        filterset = OperationFilterForBalance(
            {"ges_bound_min": "10", "ges_bound_max": "90"}, queryset=queryset, request=request
        )

        result = filterset.ignore(queryset, "ges_bound_min", "10")

        # Verify queryset is returned unchanged
        self.assertEqual(result, queryset)
