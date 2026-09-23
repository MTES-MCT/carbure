from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.viewsets import ModelViewSet

from core.filters import FiltersActionFactory
from core.pagination import TotalCountPagination
from h2.filters.h2_station import H2StationFilter
from h2.models import H2Station
from h2.permissions import HasH2AdminRights, HasHRSRights, HasHRSWriteRights
from h2.serializers import H2StationInputSerializer, H2StationSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
    ]
)
class H2StationViewSet(FiltersActionFactory(), ModelViewSet):
    queryset = H2Station.objects.all()
    serializer_class = H2StationSerializer
    permission_classes = [HasHRSRights | HasH2AdminRights]
    filterset_class = H2StationFilter
    pagination_class = TotalCountPagination
    search_fields = ["name", "site_siret", "city"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [HasHRSWriteRights()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        if HasH2AdminRights().has_permission(self.request, self):
            return queryset
        return queryset.filter(created_by=self.request.entity)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return H2StationInputSerializer
        return H2StationSerializer
