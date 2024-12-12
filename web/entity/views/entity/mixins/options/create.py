from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ValidationError

from core.models import Entity


class CreateEntityError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    ENTITY_EXISTS = "ENTITY_EXISTS"
    ENTITY_CREATION_FAILED = "ENTITY_CREATION_FAILED"


class CreateEntitySerializer(ModelSerializer):
    class Meta:
        model = Entity
        fields = ["name", "entity_type", "has_saf", "has_elec"]

    def validate_name(self, value):
        if Entity.objects.filter(name=value).exists():
            raise ValidationError(CreateEntityError.ENTITY_EXISTS)
        return value


# ViewSet
class CreateEntityActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        request=CreateEntitySerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "success"},
                description="Request successful.",
            ),
            400: OpenApiResponse(
                response={"message": ""},
                description="Bad request.",
            ),
        },
        examples=[
            OpenApiExample(
                "Success example",
                value={"status": "success"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Bad request",
                value={"message": ""},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        serializer = CreateEntitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(
                {"message": CreateEntityError.ENTITY_CREATION_FAILED},
                status=status.HTTP_400_BAD_REQUEST,
            )
