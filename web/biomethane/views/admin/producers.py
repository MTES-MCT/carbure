from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.permissions import HasDrealRights
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
    queryset = Entity.objects.filter(entity_type=Entity.BIOMETHANE_PRODUCER)
    permission_classes = [HasDrealRights]
    serializer_class = BiomethaneProducerSerializer

    def list(self, request):
        """
        List biomethane producers visible by the current DREAL entity.

        Returns producers that have production units in departments
        accessible by the DREAL.
        """
        entity = request.entity

        accessible_dept_codes = entity.get_accessible_departments().values_list("code_dept", flat=True)

        # Get producers with production units in accessible departments
        producers = (
            Entity.objects.filter(
                entity_type=Entity.BIOMETHANE_PRODUCER,
                biomethane_production_unit__department__code_dept__in=accessible_dept_codes,
            )
            .distinct()
            .order_by("name")
        )

        data = self.get_serializer(producers, many=True).data
        return Response(data)
