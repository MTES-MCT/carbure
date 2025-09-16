from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from web.biomethane.permissions import get_biomethane_permissions

from biomethane.models import BiomethaneEnergy, BiomethaneEnergyMonthlyReport
from biomethane.serializers.energy import (
    BiomethaneEnergyMonthlyReportInputSerializer,
    BiomethaneEnergyMonthlyReportSerializer,
)
from biomethane.utils import get_declaration_period


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
class BiomethaneEnergyMonthlyReportViewSet(GenericViewSet, ListModelMixin):
    queryset = BiomethaneEnergyMonthlyReport.objects.all()
    serializer_class = BiomethaneEnergyMonthlyReportSerializer
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["upsert"], self.action)

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        setattr(request, "year", get_declaration_period())

        return request

    def get_serializer_context(self):
        context = super().get_serializer_context()

        entity = getattr(self.request, "entity", None)
        year = getattr(self.request, "year", None)
        context["entity"] = entity
        context["year"] = year

        if entity and year:
            try:
                energy = BiomethaneEnergy.objects.get(producer=entity, year=year)
                context["energy"] = energy
            except BiomethaneEnergy.DoesNotExist:
                context["energy"] = None

        return context

    def get_serializer_class(self):
        if self.action == "upsert":
            return BiomethaneEnergyMonthlyReportInputSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        entity = getattr(self.request, "entity", None)
        year = getattr(self.request, "year", None) if self.action != "list" else self.request.query_params.get("year")
        return self.queryset.filter(energy__producer=entity, energy__year=year)

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
                response=BiomethaneEnergyMonthlyReportSerializer(many=True),
                description="Energy declaration monthly reports for the year",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Energy monthly reports not found for this entity and year."
            ),
        },
        description="Retrieve the energy declaration monthly reports for the current entity and year",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                description="Monthly reports created or updated successfully",
            ),
        },
        request=BiomethaneEnergyMonthlyReportInputSerializer,
        description="Create or update monthly reports for the specified energy declaration.",
    )
    def upsert(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            reports = self.get_queryset()
            status_code = status.HTTP_200_OK if reports.count() > 0 else status.HTTP_201_CREATED

            serializer.save()

            return Response(status=status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
