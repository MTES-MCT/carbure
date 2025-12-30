from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status, viewsets
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from core.models import Entity, ExternalAdminRights, UserRights
from core.permissions import HasAdminRights, HasUserRights
from entity.serializers import EntitySiteSerializer
from transactions.models import Depot, EntitySite

from .mixins import DepotActionMixin


class DepotViewSet(ListModelMixin, viewsets.GenericViewSet, DepotActionMixin):
    serializer_class = EntitySiteSerializer
    pagination_class = None
    permission_classes = [HasUserRights | HasAdminRights]

    def get_permissions(self):
        if self.action in ["add", "create_depot", "delete_depot"]:
            return [HasUserRights(role=[UserRights.ADMIN, UserRights.RW])]

        return super().get_permissions()

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
        entity = request.entity

        if entity.entity_type in [Entity.ADMIN, Entity.EXTERNAL_ADMIN] and (
            company_id := self.request.query_params.get("company_id")
        ):
            entity = Entity.objects.filter(id=company_id).first() or entity

        try:
            if entity.has_external_admin_right(ExternalAdminRights.DGDDI):
                depots = entity.get_accessible_depots()
                serializer = EntitySiteSerializer(instance=depots, many=True)
            else:
                entity_sites = EntitySite.objects.filter(entity=entity, site__in=Depot.objects.all())
                serializer = EntitySiteSerializer(instance=entity_sites, many=True)
            return Response(serializer.data)
        except Exception:
            return Response(
                {"message": "Could not find entity's delivery sites"},
                status=status.HTTP_400_BAD_REQUEST,
            )
