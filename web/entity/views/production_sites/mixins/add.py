from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.response import Response

from core.models import Entity, Pays
from entity.serializers import ProductionSiteSerializer
from transactions.models import EntitySite, ProductionSite


class ProductionSiteModelSerializer(serializers.ModelSerializer):
    country_code = serializers.CharField(required=True)

    class Meta:
        model = ProductionSite
        fields = [
            "country_code",
            "country",
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
        extra_kwargs = {
            "id": {"read_only": True},
            "country": {"required": False},
            "name": {"required": True},
            "date_mise_en_service": {"required": True},
            "ges_option": {"required": True},
            "eligible_dc": {"required": True},
            "dc_reference": {"required": False},
            "site_siret": {"required": True},
            "city": {"required": True},
            "address": {"required": True},
            "postal_code": {"required": True},
            "manager_name": {"required": True},
            "manager_phone": {"required": True},
            "manager_email": {"required": True},
        }

    def validate(self, attrs):
        attrs.pop("country_code", None)
        return attrs


class AddProductionSiteMixin:
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
        request=ProductionSiteModelSerializer,
        responses=ProductionSiteSerializer,
    )
    def create(self, request):
        # Retrieve related models
        serializer = ProductionSiteModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        country_code = request.data.get("country_code")
        entity_id = self.request.query_params.get("entity_id")
        if country_code is None:
            return Response(
                {
                    "status": "error",
                    "message": "SETTINGS_ADD_PRODUCTION_SITE_MISSING_COUNTRY_CODE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            country = Pays.objects.get(code_pays=country_code)
        except Exception:
            return Response(
                {
                    "status": "error",
                    "message": "SETTINGS_ADD_PRODUCTION_SITE_UNKNOWN_COUNTRY_CODE",
                    "extra": country_code,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            producer = Entity.objects.get(id=entity_id, entity_type="Producteur")
        except Exception:
            return Response(
                {
                    "status": "error",
                    "message": "SETTINGS_ADD_PRODUCTION_SITE_UNKNOWN_PRODUCER",
                    "extra": entity_id,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        data["country"] = country.id
        data["created_by"] = producer.id

        serializer = ProductionSiteModelSerializer(data=data)
        if not serializer.is_valid():
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            site = serializer.save()
            site.site_type = ProductionSite.PRODUCTION_BIOLIQUID
            site.save()

            EntitySite.objects.create(entity=producer, site=site)

        except Exception:
            return Response(
                {
                    "status": "error",
                    "message": "Unknown error. Please contact an administrator",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(site.natural_key())
