from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response


class RetrieveSingleObjectMixin:
    """
    Mixin for ViewSets that retrieve a single object without ID in URL.
    Uses filterset to get the object and checks object-level permissions.

    The ViewSet must have:
    - filterset_class configured
    - queryset defined
    """

    def get_object(self):
        """
        Retrieve the object using filterset and check object permissions.
        """
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get()
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Object details for the entity",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Object not found for this entity."),
        },
        description="Retrieve the object for the current entity. Returns a single object.",
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single object based on query parameters."""
        try:
            obj = self.get_object()
            data = self.get_serializer(obj, many=False).data
            return Response(data)

        except self.queryset.model.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
