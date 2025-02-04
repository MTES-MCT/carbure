from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Entity, Pays


class UpdateEntityError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    ENTITY_CREATION_FAILED = "ENTITY_CREATION_FAILED"
    REGISTRATION_ID_FORMAT_INVALID = "REGISTRATION_ID_FORMAT_INVALID"


class UpdateEntityInfoSerializer(serializers.Serializer):
    activity_description = serializers.CharField(max_length=5000, required=False, allow_blank=True)
    legal_name = serializers.CharField(max_length=128, required=False, allow_blank=True)
    registered_address = serializers.CharField(required=False, allow_blank=True)
    registered_city = serializers.CharField(required=False, allow_blank=True)
    registered_country_code = serializers.SlugRelatedField(
        queryset=Pays.objects.all(), required=False, slug_field="code_pays"
    )
    registered_zipcode = serializers.CharField(required=False, allow_blank=True)
    registration_id = serializers.CharField(max_length=64, required=False, allow_blank=True)
    sustainability_officer = serializers.CharField(max_length=256, required=False, allow_blank=True)
    sustainability_officer_email = serializers.EmailField(required=False, allow_blank=True)
    sustainability_officer_phone_number = serializers.CharField(max_length=32, required=False, allow_blank=True)
    vat_number = serializers.CharField(max_length=32, required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)


class UpdateInfoActionMixin:
    permission_classes = [IsAuthenticated]

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
        request=UpdateEntityInfoSerializer,
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
    @action(detail=False, methods=["post"], url_path="update-entity-info")
    def update_entity_info(self, request):
        serializer = UpdateEntityInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        entity_id = request.query_params.get("entity_id")
        data = serializer.validated_data

        try:
            entity = Entity.objects.get(id=entity_id)
            entity.legal_name = data.get("legal_name", entity.legal_name)
            entity.sustainability_officer_phone_number = data.get(
                "sustainability_officer_phone_number",
                entity.sustainability_officer_phone_number,
            )
            entity.registration_id = data.get("registration_id", entity.registration_id)
            entity.sustainability_officer = data.get("sustainability_officer", entity.sustainability_officer)
            entity.sustainability_officer_email = data.get(
                "sustainability_officer_email", entity.sustainability_officer_email
            )
            entity.registered_address = data.get("registered_address", entity.registered_address)
            entity.registered_zipcode = data.get("registered_zipcode", entity.registered_zipcode)
            entity.registered_city = data.get("registered_city", entity.registered_city)
            entity.registered_country = data.get("registered_country_code", entity.registered_country)
            entity.activity_description = data.get("activity_description", entity.activity_description)
            entity.website = data.get("website", entity.website)
            entity.vat_number = data.get("vat_number", entity.vat_number)
            entity.save()
        except Entity.DoesNotExist:
            return Response(
                {"message": UpdateEntityError.ENTITY_CREATION_FAILED},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"status": "success"})
