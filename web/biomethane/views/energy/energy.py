from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.filters.mixins import EntityProducerFilter, EntityProducerYearFilter
from biomethane.models.biomethane_energy import BiomethaneEnergy
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.energy.energy import (
    BiomethaneEnergyInputSerializer,
    BiomethaneEnergySerializer,
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
    ]
)
@extend_schema_view(
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                name="year",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Year of the energy declaration.",
                required=True,
            ),
        ],
    )
)
class BiomethaneEnergyViewSet(OptionalFieldsActionMixin, RetrieveSingleObjectMixin, GenericViewSet):
    queryset = BiomethaneEnergy.objects.all()
    serializer_class = BiomethaneEnergySerializer
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["upsert", "validate_energy"], self.action)

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
            return BiomethaneEnergyInputSerializer
        return super().get_serializer_class()

    def get_filterset_class(self):
        if self.action == "retrieve":
            return EntityProducerYearFilter
        elif self.action in ["upsert", "get_optional_fields"]:
            return EntityProducerFilter
        return None

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["upsert", "get_optional_fields"]:
            # force filtering by current declaration year
            queryset = queryset.filter(year=self.request.year)
        return queryset

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneEnergySerializer,
                description="Energy declaration updated successfully",
            ),
            status.HTTP_201_CREATED: OpenApiResponse(
                response=BiomethaneEnergySerializer,
                description="Energy declaration created successfully",
            ),
        },
        request=BiomethaneEnergyInputSerializer,
        description="Create or update the energy declaration for the current entity and the current year.",
    )
    def upsert(self, request, *args, **kwargs):
        if not BiomethaneAnnualDeclarationService.is_declaration_editable(request.entity, request.year):
            return Response(
                {"error": "Cannot modify energy declaration when annual declaration is already declared."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            energy = self.filter_queryset(self.get_queryset()).get()
            serializer = self.get_serializer(energy, data=request.data, partial=True)
            status_code = status.HTTP_200_OK
        except BiomethaneEnergy.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            status_code = status.HTTP_201_CREATED

        if serializer.is_valid():
            energy = serializer.save()
            return Response(status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
