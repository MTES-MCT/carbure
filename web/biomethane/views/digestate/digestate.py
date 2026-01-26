from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.filters.mixins import EntityProducerYearFilter
from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.digestate import (
    BiomethaneDigestateInputSerializer,
    BiomethaneDigestateSerializer,
)
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from biomethane.views.mixins import OptionalFieldsActionMixin
from biomethane.views.mixins.retrieve import RetrieveSingleObjectMixin


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
        OpenApiParameter(
            name="year",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Year of the energy declaration.",
            required=True,
        ),
    ]
)
class BiomethaneDigestateViewSet(OptionalFieldsActionMixin, RetrieveSingleObjectMixin, GenericViewSet):
    queryset = BiomethaneDigestate.objects.all()
    serializer_class = BiomethaneDigestateSerializer
    filterset_class = EntityProducerYearFilter
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["upsert"], self.action)

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        setattr(request, "year", request.query_params.get("year"))
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
            digestate = self.filter_queryset(self.get_queryset()).get()
            serializer = self.get_serializer(digestate, data=request.data, partial=True)
            status_code = status.HTTP_200_OK
        except BiomethaneDigestate.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            status_code = status.HTTP_201_CREATED

        if serializer.is_valid():
            digestate = serializer.save()
            return Response(status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
