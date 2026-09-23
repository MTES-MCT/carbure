import django_filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from core.filters import MultipleBooleanFilter
from h2.models import H2Station


class H2StationFilter(django_filters.FilterSet):
    entity = django_filters.AllValuesMultipleFilter(field_name="created_by__name")
    access_type = django_filters.AllValuesMultipleFilter(field_name="access_type")
    has_personal_vehicle_connector = MultipleBooleanFilter(field_name="has_personal_vehicle_connector")

    commissioning_year = extend_schema_field(OpenApiTypes.NUMBER)(
        django_filters.AllValuesMultipleFilter(field_name="commissioning_date__year")
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("site_siret", "site_siret"),
            ("distribution_capacity", "distribution_capacity"),
            ("commissioning_date", "commissioning_date"),
        )
    )

    class Meta:
        model = H2Station
        fields = [
            "access_type",
            "has_personal_vehicle_connector",
        ]
