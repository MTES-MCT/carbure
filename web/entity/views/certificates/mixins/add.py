from django.db.models.query_utils import Q
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from carbure.tasks import background_bulk_sanity_checks
from core.models import CarbureLot, Entity, EntityCertificate, GenericCertificate


class AddCertificateSerializer(serializers.Serializer):
    certificate_id = serializers.CharField(required=True)
    certificate_type = serializers.CharField(required=True)

    def validate_certificate_id(self, value):
        """Ensure the certificate_id is valid."""
        if not GenericCertificate.objects.filter(certificate_id=value).exists():
            raise serializers.ValidationError("Invalid certificate_id")
        return value

    def validate_certificate_type(self, value):
        """Ensure the certificate_type is valid."""
        if value not in dict(GenericCertificate.CERTIFICATE_TYPES):
            raise serializers.ValidationError("Invalid certificate_type")
        return value


class AddCertificateActionMixin:
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
        request=AddCertificateSerializer,
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
    @action(detail=False, methods=["post"])
    def add(self, request):
        entity_id = self.request.query_params.get("entity_id")
        serializer = AddCertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate_id = serializer.validated_data.get("certificate_id")
        certificate_type = serializer.validated_data.get("certificate_type")
        entity = Entity.objects.get(id=entity_id)

        certificate = GenericCertificate.objects.get(certificate_type=certificate_type, certificate_id=certificate_id)
        EntityCertificate.objects.update_or_create(entity=entity, certificate=certificate)
        lots = CarbureLot.objects.filter(
            Q(supplier_certificate=certificate_id) | Q(production_site_certificate=certificate_id)
        )
        background_bulk_sanity_checks(lots)

        return Response({"status": "success"})
