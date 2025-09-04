from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.models import BiomethaneEnergy, BiomethaneEnergyMonthlyReport
from biomethane.serializers.energy import (
    BiomethaneEnergyMonthlyReportInputSerializer,
    BiomethaneEnergyMonthlyReportSerializer,
)
from biomethane.utils import get_declaration_period
from core.models import Entity, UserRights
from core.permissions import HasUserRights


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
    permission_classes = [HasUserRights(entity_type=[Entity.BIOMETHANE_PRODUCER])]
    pagination_class = None

    def get_permissions(self):
        if self.action in [
            "upsert",
        ]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.BIOMETHANE_PRODUCER])]
        return super().get_permissions()

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
        year = getattr(self.request, "year", None)
        return self.queryset.filter(energy__producer=entity, energy__year=year)

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
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
