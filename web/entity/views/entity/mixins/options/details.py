from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.response import Response

from core.models import Entity
from entity.serializers import UserEntitySerializer


class EntityDetailActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="The id of the admin entity enabling the company",
                required=True,
            ),
        ],
        responses=UserEntitySerializer,
    )
    def retrieve(self, request, id=None):
        try:
            entity = Entity.objects.get(pk=id)
            serializer = UserEntitySerializer(instance=entity)
            return Response(serializer.data)
        except Entity.DoesNotExist:
            return Response(
                {"message": "Could not find entity"},
                status=status.HTTP_400_BAD_REQUEST,
            )
