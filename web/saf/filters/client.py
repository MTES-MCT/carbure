import django_filters

from core.models import Entity


class ClientFilter(django_filters.FilterSet):
    entity_id = django_filters.CharFilter(method="filter_exclude_entity_id")

    class Meta:
        model = Entity
        fields = []

    def filter_exclude_entity_id(self, queryset, name, value):
        return queryset.exclude(id=value)
