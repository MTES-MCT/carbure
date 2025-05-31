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

        application = DoubleCountingApplication.objects.prefetch_related("production").get(id=id)
        links = []
        can_download = entity.entity_type in [Entity.ADMIN, Entity.PRODUCER] or entity.has_external_admin_right(
            ExternalAdminRights.DOUBLE_COUNTING
        )

        if can_download:
            excel_link = application.download_link
            dechets_link = application.industrial_wastes_file_link

            links.append(
                {
                    "name": "APPLICATION_EXCEL",
                    "link": private_storage.url(excel_link) if excel_link else None,
                }
            )

            if application.has_industrial_waste():
                links.append(
                    {
                        "name": "INDUSTRIAL_WASTES",
                        "link": private_storage.url(dechets_link) if dechets_link else None,
                    }
                )

        return Response(AgreementDownloadLinkSerializer(links, many=True).data)
