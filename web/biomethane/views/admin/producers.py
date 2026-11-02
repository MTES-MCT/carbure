from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from biomethane.permissions import CanAccessAdminModule
from biomethane.serializers.admin.producer import BiomethaneProducerSerializer
from core.models import Entity


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
class BiomethaneProducersViewSet(GenericViewSet, ListModelMixin):
    """
    List biomethane producers visible by the current DREAL entity.

    Returns producers that have production units in departments
    accessible by the DREAL.
    """

    queryset = Entity.objects.filter(entity_type=Entity.BIOMETHANE_PRODUCER)
    permission_classes = [CanAccessAdminModule]
    serializer_class = BiomethaneProducerSerializer
    pagination_class = None

    def get_queryset(self):
        return self.queryset.filter(id__in=self.request.entity.get_allowed_entities()).order_by("name")
