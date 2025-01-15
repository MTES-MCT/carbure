import traceback

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity, EntityCertificate, GenericCertificate


class SetDefaultCertificateSerializer(serializers.Serializer):
    certificate_id = serializers.CharField(required=True)

    def validate_certificate_id(self, value):
        """Ensure the certificate_id is valid."""
        if not GenericCertificate.objects.filter(certificate_id=value).exists():
            raise serializers.ValidationError("Invalid certificate_id")
        return value


class SetDefaultCertificateActionMixin:
    @extend_schema(
        request=SetDefaultCertificateSerializer,
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
    @action(detail=False, methods=["post"], url_path="set-default")
    def set_default(self, request):
        entity_id = self.request.query_params.get("entity_id")
        serializer = SetDefaultCertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate_id = serializer.validated_data.get("certificate_id")

        try:
            link = EntityCertificate.objects.get(entity_id=entity_id, certificate__certificate_id=certificate_id)
        except Exception:
            traceback.print_exc()
            return Response(
                {
                    "status": "error",
                    "message": "Could not find certificate_id associated with your entity",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        entity = Entity.objects.get(id=entity_id)
        entity.default_certificate = link.certificate.certificate_id
        entity.save()
        return Response({"status": "success"})
