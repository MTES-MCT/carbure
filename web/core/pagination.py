from rest_framework.response import Response

from core.utils import CustomPageNumberPagination


class MetadataPageNumberPagination(CustomPageNumberPagination):
    """
    A generic pagination class that extends PageNumberPagination to include extra aggregated metadata.
    The aggregated values will be computed over the full queryset (ignoring pagination).

    To use it, set the `aggregate_fields` attribute (a dict of Django ORM aggregation expressions)
    either by subclassing or dynamically in your view. For example:

    class CustomMetadataPageNumberPagination(MetadataPageNumberPagination):
        aggregate_fields = {
            'total_volume': Sum('volume'),
            'total_ghg': Sum('ghg'),
        }

    You can also override the `get_extra_metadata` method:

    class CustomMetadataPageNumberPagination(MetadataPageNumberPagination):
        # this property should still be defined in order to generate the pagination schema correctly
        aggregate_fields = {
            'total': True
        }

        def get_extra_metadata(self):
            metadata = {'total': 0}
            for item in self.queryset:
                metadata.total += item.volume
            return metadata
    """

    aggregate_fields = {}

    def paginate_queryset(self, queryset, request, view=None):
        # Save the full queryset for later use in metadata calculation.
        self.queryset = queryset
        return super().paginate_queryset(queryset, request, view=view)

    def get_extra_metadata(self):
        metadata = {}
        if self.aggregate_fields and hasattr(self, "queryset"):
            metadata = self.queryset.aggregate(**self.aggregate_fields)
        return metadata

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                **self.get_extra_metadata(),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        response_schema = super().get_paginated_response_schema(schema)
        extra_properties = {key: {"type": "number"} for key in self.aggregate_fields.keys()}
        response_schema["properties"].update(extra_properties)
        return response_schema
