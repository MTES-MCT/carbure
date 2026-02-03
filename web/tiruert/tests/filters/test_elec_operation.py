from unittest.mock import Mock

from django.db.models import Q
from django.http import QueryDict
from django.test import RequestFactory, SimpleTestCase

from tiruert.filters.elec_operation import ElecOperationFilter
from tiruert.models import ElecOperation


class ElecOperationFilterTest(SimpleTestCase):
    """Unit tests for ElecOperationFilter using mocked querysets (no DB I/O)."""

    def setUp(self):
        self.factory = RequestFactory()

        qs = Mock()
        qs.model = ElecOperation
        qs.filter.return_value = qs
        qs.distinct.return_value = qs
        qs.all.return_value = qs

        self.queryset = qs

    def create_filter_set(self, query_string: str):
        request = self.factory.get(f"/test/?{query_string}")
        request.query_params = request.GET
        data = QueryDict(query_string)
        return ElecOperationFilter(data, queryset=self.queryset, request=request)

    def test_filter_status_accepts_multiple_values(self):
        filter_set = self.create_filter_set("status=PENDING&status=ACCEPTED")

        filter_set.filter_status(self.queryset, "status", None)

        expected = Q(status__in=["PENDING", "ACCEPTED"])
        self.queryset.filter.assert_called_once_with(expected)

    def test_filter_type_credit_filters_by_credited_entity(self):
        filter_set = self.create_filter_set("type=CREDIT&entity_id=5")

        filter_set.filter_type(self.queryset, "type", "CREDIT")

        self.queryset.filter.assert_called_once_with(type__in=["CESSION", "ACQUISITION_FROM_CPO"], credited_entity_id="5")

    def test_filter_type_debit_filters_by_debited_entity(self):
        filter_set = self.create_filter_set("type=DEBIT&entity_id=7")

        filter_set.filter_type(self.queryset, "type", "DEBIT")

        self.queryset.filter.assert_called_once_with(type__in=["CESSION", "TENEUR"], debited_entity_id="7")

    def test_filter_type_unknown_returns_queryset_unchanged(self):
        filter_set = self.create_filter_set("type=UNKNOWN&entity_id=1")

        result = filter_set.filter_type(self.queryset, "type", "UNKNOWN")

        self.assertIs(result, self.queryset)
        self.queryset.filter.assert_not_called()

    def test_filter_period_combines_periods_with_or(self):
        filter_set = self.create_filter_set("period=202401&period=202403")

        filter_set.filter_period(self.queryset, "period", "202401")

        expected = Q(created_at__year="2024", created_at__month="01") | Q(created_at__year="2024", created_at__month="03")
        self.queryset.filter.assert_called_once()
        called_q = self.queryset.filter.call_args[0][0]
        self.assertEqual(called_q, expected)

    def test_filter_operation_handles_aliases(self):
        filter_set = self.create_filter_set("entity_id=9&operation=ACQUISITION&operation=CESSION&operation=TENEUR")

        filter_set.filter_operation(self.queryset, "operation", None)

        expected = (
            Q(type="CESSION", credited_entity_id="9") | Q(type="CESSION", debited_entity_id="9") | Q(type__in=["TENEUR"])
        )
        self.queryset.filter.assert_called_once()
        called_q = self.queryset.filter.call_args[0][0]
        self.assertEqual(called_q, expected)

    def test_filter_operation_specific_type_only(self):
        filter_set = self.create_filter_set("entity_id=2&operation=TENEUR")

        filter_set.filter_operation(self.queryset, "operation", None)

        expected = Q(type__in=["TENEUR"])
        self.queryset.filter.assert_called_once_with(expected)

    def test_filter_entity_filters_credit_or_debit(self):
        filter_set = self.create_filter_set("entity_id=42")

        filter_set.filter_entity(self.queryset, "entity_id", "42")

        expected = Q(credited_entity="42") | Q(debited_entity="42")
        self.queryset.filter.assert_called_once_with(expected)
        self.queryset.distinct.assert_called_once()

    def test_filter_from_to_filters_by_names(self):
        request = self.factory.get("/test/?from_to=A&from_to=B")
        request.query_params = request.GET
        data = QueryDict("from_to=A&from_to=B")
        filter_set = ElecOperationFilter(data, queryset=self.queryset, request=request)

        filter_set.filter_from_to(self.queryset, "from_to", None)

        expected = Q(credited_entity__name__in=["A", "B"]) | Q(debited_entity__name__in=["A", "B"])
        self.queryset.filter.assert_called_once_with(expected)
        self.queryset.distinct.assert_called_once()
