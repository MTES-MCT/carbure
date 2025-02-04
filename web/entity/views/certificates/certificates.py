from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response

from certificates.models import ProductionSiteCertificate
from core.models import Entity, EntityCertificate, ExternalAdminRights, UserRights
from core.serializers import EntityCertificateSerializer
from saf.permissions import HasUserRights
from saf.permissions.user_rights import HasAdminRights, OrPermission

from .mixins import ActionMixin


class EntityCertificateViewSet(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet, ActionMixin):
    serializer_class = EntityCertificateSerializer
    pagination_class = None
    permission_classes = []

    def get_queryset(self):
        return EntityCertificate.objects.order_by("-added_dt", "checked_by_admin").select_related("entity", "certificate")

    def get_permissions(self):
        # TODO fix permissions if needed
        if self.action in ["add", "delete", "update_certificate"]:
            return (
                HasUserRights(
                    [UserRights.ADMIN, UserRights.RW],
                    [Entity.OPERATOR, Entity.PRODUCER, Entity.TRADER],
                ),
            )

        if self.action in ["set_default"]:
            return (
                HasUserRights(
                    None,
                    [Entity.OPERATOR, Entity.PRODUCER, Entity.TRADER],
                ),
            )

        if self.action in ["check_entity", "reject_entity"]:
            return [HasAdminRights(allow_external=[ExternalAdminRights.DOUBLE_COUNTING])]

        return [
            OrPermission(
                lambda: HasUserRights(None, [Entity.OPERATOR, Entity.PRODUCER, Entity.TRADER]),
                lambda: HasAdminRights(allow_external=[ExternalAdminRights.DOUBLE_COUNTING]),
            )
        ]

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
            OpenApiParameter(
                "production_site_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Production site ID",
                required=False,
            ),
            OpenApiParameter(
                "query",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Search within the field `certificate_id`",
                required=False,
            ),
        ],
        responses=EntityCertificateSerializer(many=True),
    )
    def list(self, request):
        entity_id = self.request.query_params.get("entity_id")
        query = self.request.query_params.get("query", None)
        production_site_id = self.request.query_params.get("production_site_id")
        entity = Entity.objects.get(id=entity_id)
        queryset = self.get_queryset()
        if query:
            queryset = queryset.filter(certificate__certificate_id__icontains=query)

        if entity.entity_type == Entity.ADMIN:
            company_id = self.request.query_params.get("company_id")
            if company_id:
                queryset = queryset.filter(entity_id=company_id)
        else:
            queryset = queryset.filter(entity=entity)

        certificates = list(queryset)

        if production_site_id:
            links = ProductionSiteCertificate.objects.filter(entity=entity, production_site_id=production_site_id)
            certificates = [link.certificate for link in links]

        serializer = EntityCertificateSerializer(certificates, many=True)
        return Response(serializer.data)
