from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.models import Entity, ExternalAdminRights
from doublecount.serializers import (
    EntitySerializer,
)
from entity.services.enable_entity import enable_entity as enable_entity_service
from entity.services.get_administrated_entities import get_administrated_entities
from saf.permissions.user_rights import HasAdminRights
from saf.serializers.schema import ErrorResponseSerializer


class EntityViewSet(ViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="The id of the admin entity enabling the company",
                required=True,
            ),
        ],
        responses={200: OpenApiTypes.ANY, 400: ErrorResponseSerializer},
    )
    @permission_classes(
        [IsAuthenticated, HasAdminRights(allow_external=[ExternalAdminRights.AIRLINE, ExternalAdminRights.ELEC])]
    )
    @action(
        methods=["post"],
        detail=True,
        url_path="enable",
        url_name="enable",
    )
    def enable_entity(self, request, pk=None):
        entity_id = request.query_params.get("entity_id")

        admin_entity = Entity.objects.get(pk=entity_id)
        administrated_entities = get_administrated_entities(admin_entity)

        try:
            entity_to_enable = administrated_entities.get(pk=pk)
        except Entity.DoesNotExist:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        enable_entity_service(entity_to_enable, request)

        return Response({}, status=status.HTTP_200_OK)
