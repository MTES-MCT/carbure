from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.filters.digestate import BiomethaneDigestateFilter, BiomethaneDigestateRetrieveFilter
from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.digestate import (
    BiomethaneDigestateInputSerializer,
    BiomethaneDigestateSerializer,
)
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from biomethane.views.mixins import OptionalFieldsActionMixin


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
    ]
)
class BiomethaneDigestateViewSet(GenericViewSet, OptionalFieldsActionMixin):
    queryset = BiomethaneDigestate.objects.all()
    serializer_class = BiomethaneDigestateSerializer
    filterset_class = BiomethaneDigestateFilter
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["upsert", "validate_digestate"], self.action)

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        setattr(request, "year", BiomethaneAnnualDeclarationService.get_declaration_period())
        return request

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        context["year"] = getattr(self.request, "year", None)
        return context

    def get_serializer_class(self):
        if self.action == "upsert":
            return BiomethaneDigestateInputSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            return BiomethaneDigestateRetrieveFilter(self.request.GET, queryset=queryset).qs
        elif self.action in ["upsert", "get_optional_fields"]:
            # force filtering by current declaration year
            queryset = queryset.filter(year=self.request.year)
            return BiomethaneDigestateFilter(self.request.GET, queryset=queryset).qs
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="year",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Declaration year.",
                required=True,
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneDigestateSerializer,
                description="Digestate details for the entity",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Digestate not found for this entity."),
        },
        description="Retrieve the digestate for the current entity and the current year. Returns a single digestate object.",
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            digestate = self.get_queryset().get()
            data = self.get_serializer(digestate, many=False).data
            return Response(data)

        except BiomethaneDigestate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneDigestateSerializer,
                description="Digestate updated successfully",
            ),
            status.HTTP_201_CREATED: OpenApiResponse(
                response=BiomethaneDigestateSerializer,
                description="Digestate created successfully",
            ),
        },
        request=BiomethaneDigestateInputSerializer,
        description="Create or update the digestate for the current entity (upsert operation).",
    )
    def upsert(self, request, *args, **kwargs):
        if not BiomethaneAnnualDeclarationService.is_declaration_editable(request.entity, request.year):
            return Response(
                {"error": "Cannot modify digestate declaration when annual declaration is already declared."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            digestate = self.get_queryset().get()
            serializer = self.get_serializer(digestate, data=request.data, partial=True)
            status_code = status.HTTP_200_OK
        except BiomethaneDigestate.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            status_code = status.HTTP_201_CREATED

        if serializer.is_valid():
            digestate = serializer.save()
            return Response(status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
