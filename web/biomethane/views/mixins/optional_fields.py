from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class OptionalFieldsActionMixin:
    """
    Mixin to add an optional_fields action to a ViewSet.

    The ViewSet's model must have an optional_fields property.
    Returns the optional fields for the first object in the queryset.
    """

    @extend_schema(
        responses={
            status.HTTP_200_OK: {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of optional field names",
            },
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found for this entity."),
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="optional-fields",
    )
    def get_optional_fields(self, request, *args, **kwargs):
        """Return the optional fields for the first object in the queryset."""
        try:
            instance = self.get_queryset().get()
            return Response(instance.optional_fields, status=status.HTTP_200_OK)
        except self.get_queryset().model.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
