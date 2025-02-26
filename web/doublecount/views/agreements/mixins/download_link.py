from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response

from core.models import Entity, ExternalAdminRights
from doublecount.models import DoubleCountingApplication
from doublecount.utils import generate_presigned_url


class AgreementDownloadLinkSerializer(serializers.Serializer):
    download_link = serializers.URLField(required=False)


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
        responses=AgreementDownloadLinkSerializer,
    )
    @action(detail=True, methods=["GET"], url_path="download-link")
    def download_link(self, request, id=None):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)

        application = DoubleCountingApplication.objects.get(id=id)

        if entity.entity_type in [Entity.ADMIN, Entity.PRODUCER] or entity.has_external_admin_right(
            ExternalAdminRights.DOUBLE_COUNTING
        ):
            download_link = generate_presigned_url(application.download_link)
        else:
            download_link = None

        return Response({"download_link": download_link})
