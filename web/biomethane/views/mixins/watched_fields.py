from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class WatchedFieldsActionMixin:
    """
    Mixin to add a watched_fields action to a ViewSet.

    The ViewSet must implement get_queryset() and the model must have a watched_fields property.
    Returns the watched fields for a single object or an empty list if not found.
    """

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response={"type": "array", "items": {"type": "string"}},
                description="List of watched fields",
            ),
        },
    )
    @action(detail=False, methods=["get"], url_path="watched-fields")
    def watched_fields(self, request, *args, **kwargs):
        try:
            obj = self.filter_queryset(self.get_queryset()).get()
            watched_fields = obj.watched_fields
        except self.queryset.model.DoesNotExist:
            watched_fields = []

        return Response(watched_fields)
