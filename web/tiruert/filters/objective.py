from datetime import datetime

from django_filters import CharFilter, DateFilter, FilterSet

# from drf_spectacular.utils import extend_schema_field
# from rest_framework.serializers import CharField, ChoiceField, ListField


class ObjectiveFilter(FilterSet):
    entity_id = CharFilter(method="filter_entity")
    year = DateFilter(method="filter_year", initial=datetime.now().year)

    def filter_entity(self, queryset, name, value):
        return queryset.filter(operator_id=value)

    def filter_year(self, queryset, name, value):
        return queryset.filter(year=value)
