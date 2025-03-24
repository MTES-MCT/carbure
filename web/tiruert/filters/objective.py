from django.utils import timezone
from django_filters import CharFilter, FilterSet

# from drf_spectacular.utils import extend_schema_field
# from rest_framework.serializers import CharField, ChoiceField, ListField


class ObjectiveFilter(FilterSet):
    year = CharFilter(field_name="year", initial=timezone.now().year)
