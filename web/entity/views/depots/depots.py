from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status, viewsets
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from core.models import Entity, UserRights
from entity.serializers import EntitySiteSerializer
from saf.permissions import HasAdminRights, HasUserRights
from saf.permissions.user_rights import OrPermission
from transactions.models import Depot, EntitySite

from .mixins import DepotActionMixin


class DepotViewSet(ListModelMixin, viewsets.GenericViewSet, DepotActionMixin):
    serializer_class = EntitySiteSerializer
    pagination_class = None
    permission_classes = []

    def get_permissions(self):
        # TODO fix permissions if needed
        if self.action in [
            "add",
            "create_depot",
            "delete_depot",
        ]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW], None)]

        return [OrPermission(lambda: HasUserRights(), lambda: HasAdminRights(allow_external=[]))]

    def get_queryset(self):
        return EntitySite.objects.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
            OpenApiParameter(
                "company_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Compay ID, Admin only",
                required=False,
            ),
        ],
        responses=EntitySiteSerializer(many=True),
    )
    def list(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        if entity.entity_type == Entity.ADMIN:
            entity_id = self.request.query_params.get("company_id")

        entity = Entity.objects.get(id=entity_id)
        try:
            ds = EntitySite.objects.filter(entity=entity, site__in=Depot.objects.filter(is_enabled=True))
            serializer = EntitySiteSerializer(instance=ds, many=True)
            return Response(serializer.data)
        except Exception:
            return Response(
                {
                    "message": "Could not find entity's delivery sites",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
