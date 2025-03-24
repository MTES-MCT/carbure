from django.utils import timezone
from django_filters import DateFilter, FilterSet

# from drf_spectacular.utils import extend_schema_field
# from rest_framework.serializers import CharField, ChoiceField, ListField


class ObjectiveFilter(FilterSet):
    year = DateFilter(field_name="year", lookup_expr="exact", initial=timezone.now().year)
