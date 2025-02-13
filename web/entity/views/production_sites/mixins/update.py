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

from core.models import Pays
from transactions.models import ProductionSite


class UpdateProductionSiteModelSerializer(serializers.ModelSerializer):
    country_code = serializers.CharField(required=True)

    class Meta:
        model = ProductionSite
        fields = [
            "country_code",
            "name",
            "date_mise_en_service",
            "ges_option",
            "site_siret",
            "postal_code",
            "manager_name",
            "manager_phone",
            "manager_email",
            "city",
            "address",
            "eligible_dc",
            "dc_reference",
            "created_by",
        ]

    def validate(self, attrs):
        attrs.pop("country_code", None)
        return attrs


class UpdateProductionSiteMixin:
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
        request=UpdateProductionSiteModelSerializer,
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
    @action(detail=True, methods=["post"], url_path="update")
    def update_item(self, request, id=None):
        # Retrieve related models
        psite = ProductionSite.objects.get(id=id)
        serializer = UpdateProductionSiteModelSerializer(instance=psite, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        psite = serializer.save()
        country_code = request.data.get("country_code")
        if country_code:
            try:
                country = Pays.objects.get(code_pays=country_code)
                psite.country = country
                psite.save()
            except Exception:
                return Response({"status": "error", "message": "Unknown country"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "success"})
