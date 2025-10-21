from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.filters.energy import BiomethaneEnergyFilter, BiomethaneEnergyRetrieveFilter
from biomethane.models.biomethane_energy import BiomethaneEnergy
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.energy.energy import (
    BiomethaneEnergyInputSerializer,
    BiomethaneEnergySerializer,
)
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from biomethane.utils import get_declaration_period
from biomethane.views import OptionalFieldsActionMixin


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
class BiomethaneEnergyViewSet(GenericViewSet, OptionalFieldsActionMixin):
    queryset = BiomethaneEnergy.objects.all()
    serializer_class = BiomethaneEnergySerializer
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["upsert", "validate_energy"], self.action)

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        setattr(request, "year", get_declaration_period())
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

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            return BiomethaneEnergyRetrieveFilter(self.request.GET, queryset=queryset).qs
        elif self.action in ["upsert", "get_optional_fields"]:
            # force filtering by current declaration year
            queryset = queryset.filter(year=self.request.year)
            return BiomethaneEnergyFilter(self.request.GET, queryset=queryset).qs
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
                response=BiomethaneEnergySerializer,
                description="Energy declaration details for the entity",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Energy not found for this entity."),
        },
        description="Retrieve the energy declaration for the current entity and year. Returns a single energy object.",
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            energy = self.get_queryset().get()
            data = self.get_serializer(energy, many=False).data
            return Response(data)

        except BiomethaneEnergy.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

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
            energy = self.get_queryset().get()
            serializer = self.get_serializer(energy, data=request.data, partial=True)
            status_code = status.HTTP_200_OK
        except BiomethaneEnergy.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            status_code = status.HTTP_201_CREATED

        if serializer.is_valid():
            energy = serializer.save()
            return Response(status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
