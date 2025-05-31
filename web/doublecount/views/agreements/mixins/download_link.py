from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response

from core import private_storage
from core.models import Entity, ExternalAdminRights
from doublecount.models import DoubleCountingApplication


class AgreementDownloadLinkSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    link = serializers.URLField(required=False)


class AgreementDownloadLinkMixin(RetrieveModelMixin):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        responses=AgreementDownloadLinkSerializer(many=True),
    )
    @action(detail=True, methods=["GET"], url_path="download-link")
    def download_link(self, request, id=None):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)

        application = DoubleCountingApplication.objects.get(id=id)
        links = []
        can_download = entity.entity_type in [Entity.ADMIN, Entity.PRODUCER] or entity.has_external_admin_right(
            ExternalAdminRights.DOUBLE_COUNTING
        )

        if can_download:
            links = [
                {
                    "name": "APPLICATION_EXCEL",
                    "link": private_storage.url(application.download_link) if application.download_link else None,
                },
                {
                    "name": "INDUSTRIAL_WASTES",
                    "link": private_storage.url(application.industrial_wastes_file_link)
                    if application.industrial_wastes_file_link
                    else None,
                },
            ]

        return Response(AgreementDownloadLinkSerializer(links, many=True).data)
