from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from certificates.models import ProductionSiteCertificate
from core.models import Entity, EntityCertificate, GenericCertificate


class UpdateCertificateSerializer(serializers.Serializer):
    old_certificate_id = serializers.CharField(required=True)
    old_certificate_type = serializers.CharField(required=True)
    new_certificate_id = serializers.CharField(required=True)
    new_certificate_type = serializers.CharField(required=True)

    def validate_old_certificate_id(self, value):
        """Ensure the old_certificate_id is valid."""
        if not GenericCertificate.objects.filter(certificate_id=value).exists():
            raise serializers.ValidationError("Invalid old_certificate_id")
        return value

    def validate_new_certificate_type(self, value):
        """Ensure the new_certificate_type is valid."""
        if value not in dict(GenericCertificate.CERTIFICATE_TYPES):
            raise serializers.ValidationError("Invalid new_certificate_type")
        return value


class UpdateCertificateActionMixin:
    @extend_schema(
        request=UpdateCertificateSerializer,
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
    @action(detail=False, methods=["post"], url_path="update-certificate")
    def update_certificate(self, request):
        entity_id = self.request.query_params.get("entity_id")
        serializer = UpdateCertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_certificate_id = serializer.validated_data.get("old_certificate_id")

        new_certificate_id = serializer.validated_data.get("new_certificate_id")
        new_certificate_type = serializer.validated_data.get("new_certificate_type")
        entity = Entity.objects.get(id=entity_id)

        try:
            new_certificate = GenericCertificate.objects.get(
                certificate_type=new_certificate_type, certificate_id=new_certificate_id
            )
        except Exception:
            return Response(
                {"message": "Could not find new certificate"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            old_certificate = EntityCertificate.objects.get(entity=entity, certificate__certificate_id=old_certificate_id)
        except Exception:
            return Response(
                {"message": "Could not find old certificate"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj, _ = EntityCertificate.objects.update_or_create(entity=entity, certificate=new_certificate)
        ProductionSiteCertificate.objects.filter(entity=entity, certificate=old_certificate).update(certificate=obj)
        old_certificate.has_been_updated = True
        old_certificate.save()
        return Response({"status": "success"})
