from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from biomethane.filters.digestate import BiomethaneDigestateFilter
from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.serializers.digestate import BiomethaneDigestateSerializer
from core.models import Entity
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
        OpenApiParameter(
            "year",
            OpenApiTypes.INT,
            OpenApiParameter.QUERY,
            description="Year",
            required=True,
        ),
    ]
)
class BiomethaneDigestateViewSet(ModelViewSet):
    queryset = BiomethaneDigestate.objects.all()
    serializer_class = BiomethaneDigestateSerializer
    permission_classes = [HasUserRights(entity_type=[Entity.BIOMETHANE_PRODUCER])]
    filterset_class = BiomethaneDigestateFilter
    pagination_class = None

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneDigestateSerializer,
                description="Digestate details for the entity",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Digestate not found for this entity."),
        },
        description="Retrieve the digestate for the current entity and the current year. Returns a single digestate object.",
    )
    def retrieve(self, request, *args, **kwargs):
        year = request.query_params.get("year")
        try:
            digestate = BiomethaneDigestate.objects.get(producer=request.entity, year=year)
            data = self.get_serializer(digestate, many=False).data
            return Response(data)

        except BiomethaneDigestate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
