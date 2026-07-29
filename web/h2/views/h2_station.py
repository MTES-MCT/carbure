from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.viewsets import ModelViewSet

from h2.models import H2Station
from h2.permissions import HasHRSRights, HasHRSWriteRights
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
class H2StationViewSet(ModelViewSet):
    queryset = H2Station.objects.all()
    serializer_class = H2StationSerializer
    permission_classes = [HasHRSRights]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [HasHRSWriteRights()]
        return super().get_permissions()

    def get_queryset(self):
        return self.queryset.filter(created_by=self.request.entity)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return H2StationInputSerializer
        return H2StationSerializer
