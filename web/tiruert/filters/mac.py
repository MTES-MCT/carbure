from django.utils import timezone
from django_filters import CharFilter, FilterSet, NumberFilter

# from drf_spectacular.utils import extend_schema_field
# from rest_framework.serializers import CharField, ChoiceField, ListField


class MacFilter(FilterSet):
    entity_id = CharFilter(field_name="operator_id", lookup_expr="exact")
    year = NumberFilter(field_name="year", lookup_expr="exact", initial=timezone.now().year)
