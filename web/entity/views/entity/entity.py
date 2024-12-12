from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.models import Entity, ExternalAdminRights, UserRights
from doublecount.serializers import EntitySerializer
from entity.services.enable_entity import enable_entity as enable_entity_service
from entity.services.get_administrated_entities import get_administrated_entities
from saf.permissions import HasUserRights
from saf.permissions.user_rights import HasAdminRights

from .mixins import EntityActionMixin


class EmptyResponseSerializer(serializers.Serializer):
    empty = serializers.CharField(required=False)


class EntityViewSet(ViewSet, EntityActionMixin):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    lookup_field = "id"

    def get_permissions(self):
        # TODO fix permissions if needed
        if self.action in [
            "direct_deliveries",
            "elec",
            "release_for_consumption",
            "stocks",
            "trading",
            "preferred_unit",
        ]:
            return [
                IsAuthenticated(),
                HasUserRights(
                    [UserRights.ADMIN, UserRights.RW],
                    [Entity.PRODUCER, Entity.OPERATOR, Entity.TRADER],
                ),
            ]
        if self.action in [
            "update_entity_info",
        ]:
            return [
                IsAuthenticated(),
                HasUserRights(
                    [UserRights.ADMIN, UserRights.RW],
                    [Entity.PRODUCER, Entity.OPERATOR],
                ),
            ]
        if self.action == "get_entity_stats":
            return [
                IsAuthenticated(),
                HasUserRights([UserRights.ADMIN, UserRights.RW], []),
            ]
        if self.action in ["list", "retrieve", "create"]:
            return [
                HasAdminRights(
                    allow_external=[
                        ExternalAdminRights.AIRLINE,
                        ExternalAdminRights.ELEC,
                        ExternalAdminRights.DOUBLE_COUNTING,
                    ]
                )
            ]

        return super().get_permissions()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="The id of the admin entity enabling the company",
                required=True,
            ),
        ],
        request=EmptyResponseSerializer,
        responses=EmptyResponseSerializer,
    )
    @permission_classes(
        [
            IsAuthenticated,
            HasAdminRights(allow_external=[ExternalAdminRights.AIRLINE, ExternalAdminRights.ELEC]),
        ]
    )
    @action(
        methods=["post"],
        detail=True,
        url_path="enable",
        url_name="admin-enable",
    )
    def enable_entity(self, request, id=None):
        entity_id = request.query_params.get("entity_id")

        admin_entity = Entity.objects.get(pk=entity_id)
        administrated_entities = get_administrated_entities(admin_entity)

        try:
            entity_to_enable = administrated_entities.get(pk=id)
        except Entity.DoesNotExist:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        enable_entity_service(entity_to_enable, request)

        return Response({}, status=status.HTTP_200_OK)
