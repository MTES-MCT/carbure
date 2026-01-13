from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.filters.energy_monthly_report import BiomethaneEnergyMonthlyReportYearFilter
from biomethane.models import BiomethaneEnergyMonthlyReport
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.energy import (
    BiomethaneEnergyMonthlyReportInputSerializer,
    BiomethaneEnergyMonthlyReportSerializer,
)
from biomethane.views.mixins import ListWithObjectPermissionsMixin


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
class BiomethaneEnergyMonthlyReportViewSet(ListWithObjectPermissionsMixin, GenericViewSet, ListModelMixin):
    queryset = BiomethaneEnergyMonthlyReport.objects.all()
    filterset_class = BiomethaneEnergyMonthlyReportYearFilter
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["upsert"], self.action)

    def get_permission_object(self, first_obj):
        """Check permissions on the energy of the monthly reports."""
        return first_obj.energy if first_obj else None

    def get_serializer_class(self):
        if self.action == "upsert":
            return BiomethaneEnergyMonthlyReportInputSerializer
        return BiomethaneEnergyMonthlyReportSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["energy_instance"] = self.queryset.first().energy if self.queryset.exists() else None
        print("context:", context["energy_instance"])
        return context

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                description="Monthly reports created successfully",
            ),
            status.HTTP_200_OK: OpenApiResponse(
                description="Monthly reports updated successfully",
            ),
        },
        request=BiomethaneEnergyMonthlyReportInputSerializer,
        description="Create or update monthly reports for the specified energy declaration.",
    )
    def upsert(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            reports = self.filter_queryset(self.get_queryset())
            status_code = status.HTTP_200_OK if reports.count() > 0 else status.HTTP_201_CREATED

            serializer.save()

            return Response(status=status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
