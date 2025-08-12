from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from biomethane.models import BiomethaneDigestateStorage
from biomethane.serializers.digestate_storage import (
    BiomethaneDigestateStorageAddSerializer,
    BiomethaneDigestateStoragePatchSerializer,
    BiomethaneDigestateStorageSerializer,
)
from core.models import Entity
from core.permissions import HasUserRights


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
        OpenApiParameter(
            name="id",
            type=int,
            location=OpenApiParameter.PATH,
            description="Digestate storage unit ID.",
        ),
    ]
)
class BiomethaneDigestateStorageViewSet(ModelViewSet):
    serializer_class = BiomethaneDigestateStorageSerializer
    permission_classes = [IsAuthenticated, HasUserRights(None, [Entity.BIOMETHANE_PRODUCER])]
    pagination_class = None

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return BiomethaneDigestateStorage.objects.none()
        return BiomethaneDigestateStorage.objects.filter(producer=self.request.entity)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action == "create":
            return BiomethaneDigestateStorageAddSerializer
        elif self.action in ["update", "partial_update"]:
            return BiomethaneDigestateStoragePatchSerializer
        return BiomethaneDigestateStorageSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneDigestateStorageSerializer(many=True),
                description="List of digestate storage units for the entity",
            ),
        },
        description="Retrieve all digestate storage units for the current entity.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=BiomethaneDigestateStorageSerializer,
                description="Digestate storage unit created successfully",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data provided"),
        },
        description="Create a new digestate storage unit for the current entity.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneDigestateStorageSerializer,
                description="Digestate storage unit updated successfully",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data provided"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Digestate storage unit not found"),
        },
        description="Update an existing digestate storage unit.",
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Digestate storage unit deleted successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Digestate storage unit not found"),
        },
        description="Delete a digestate storage unit.",
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
