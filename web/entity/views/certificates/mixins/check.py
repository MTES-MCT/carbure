from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from carbure.tasks import background_bulk_scoring
from core.models import CarbureLot, EntityCertificate


class CheckCertificateSerializer(serializers.Serializer):
    certificate_id = serializers.IntegerField(required=True)

    def validate_certificate_id(self, value):
        """Ensure the certificate_id is valid."""
        if not EntityCertificate.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid certificate_id")
        return value


class CheckCertificateActionMixin:
    @extend_schema(
        request=CheckCertificateSerializer,
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
    @action(detail=False, methods=["post"], url_path="check-entity")
    def check_entity(self, request):
        serializer = CheckCertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate_id = serializer.validated_data.get("certificate_id")

        try:
            ec = EntityCertificate.objects.get(id=certificate_id)
            ec.checked_by_admin = True
            ec.rejected_by_admin = False
            ec.save()
            slots = CarbureLot.objects.filter(
                carbure_supplier=ec.entity,
                supplier_certificate=ec.certificate.certificate_id,
            )
            plots = CarbureLot.objects.filter(
                carbure_producer=ec.entity,
                production_site_certificate=ec.certificate.certificate_id,
            )
            background_bulk_scoring(list(slots) + list(plots))
            return Response({"status": "success"})
        except Exception:
            return Response(
                {"status": "error", "message": "Could not mark certificate as checked"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
