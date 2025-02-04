from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from certificates.models import ProductionSiteCertificate
from core.models import Entity, EntityCertificate
from transactions.models import ProductionSite


class SetCertificateSerializer(serializers.Serializer):
    certificate_ids = serializers.ListField(child=serializers.CharField(), required=True)


class SetCertificateActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        request=SetCertificateSerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "success"},
                description="Request successful.",
            ),
            400: OpenApiResponse(
                response={"message": ""},
                description="Bad request.",
            ),
        },
        examples=[
            OpenApiExample(
                "Success example",
                value={"status": "success"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Bad request",
                value={"message": ""},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    @action(detail=True, methods=["post"], url_path="set-certificates")
    def set_certificates(self, request, id=None):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        serializer = SetCertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate_ids = serializer.validated_data["certificate_ids"]
        production_site = ProductionSite.objects.get(id=id)
        ProductionSiteCertificate.objects.filter(entity=entity, production_site=production_site).delete()
        for certificate_id in certificate_ids:
            try:
                link = EntityCertificate.objects.get(entity_id=entity_id, certificate__certificate_id=certificate_id)
            except EntityCertificate.DoesNotExist:
                return Response(
                    {"message": "Certificate %s is not associated with your entity" % (certificate_id)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ProductionSiteCertificate.objects.update_or_create(
                entity=entity, production_site=production_site, certificate=link
            )
        return Response({"status": "success"})
