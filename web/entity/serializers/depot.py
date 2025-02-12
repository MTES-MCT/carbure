from django.core.exceptions import ValidationError
from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import Entity, Pays
from core.serializers import UserEntitySerializer as EntityUserEntitySerializer
from transactions.models import Depot, EntitySite, ProductionSite

from .users import PaysSerializer


class CreateDepotSerializer(serializers.ModelSerializer):
    country_code = serializers.SlugRelatedField(slug_field="code_pays", queryset=Pays.objects.all(), write_only=True)
    entity_id = serializers.SlugRelatedField(slug_field="id", queryset=Entity.objects.all(), write_only=True)
    depot_id = serializers.CharField(source="customs_id")
    depot_type = serializers.CharField(source="site_type")
    ownership_type = serializers.ChoiceField(choices=EntitySite.TYPE_OWNERSHIP, required=True)
    blending_is_outsourced = serializers.BooleanField(default=False, required=False)
    blending_entity_id = serializers.IntegerField(default=None, required=False)

    class Meta:
        model = Depot
        fields = "__all__"

    def create(self, validated_data):
        with transaction.atomic():
            validated_data["country"] = validated_data.pop("country_code")
            validated_data["created_by"] = validated_data.pop("entity_id")
            validated_data["is_enabled"] = False

            # Data for entity_site instance
            entity_site_data = {
                "ownership_type": validated_data.pop("ownership_type"),
                "blending_is_outsourced": validated_data.pop("blending_is_outsourced"),
                "entity": validated_data["created_by"],
                # "status": EntitySite.PENDING,
            }
            blending_entity_id = validated_data.pop("blending_entity_id")
            blender = None

            if entity_site_data["blending_is_outsourced"]:
                try:
                    blender = Entity.objects.get(id=blending_entity_id, entity_type=Entity.OPERATOR)
                except Exception:
                    raise serializers.ValidationError({"status": "error", "message": "Could not find outsourcing blender"})
            entity_site_data["blender"] = blender

            depot_instance = Depot(**validated_data)
            entity_site_instance = EntitySite(**entity_site_data)

            try:
                depot_instance.full_clean()
            except ValidationError as e:
                raise serializers.ValidationError(e.message_dict)

            depot_instance.save()
            entity_site_instance.site = depot_instance
            entity_site_instance.save()

            return depot_instance


class EntityDepotSerializer(serializers.ModelSerializer):
    country = PaysSerializer()

    class Meta:
        model = Depot
        fields = [
            "customs_id",
            "name",
            "city",
            "country",
            "site_type",
            "address",
            "postal_code",
            "electrical_efficiency",
            "thermal_efficiency",
            "useful_temperature",
            "is_enabled",
        ]


class ProductionSiteCertificateSertificate(serializers.ModelSerializer):
    certificate_id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Depot
        fields = ["type", "certificate_id"]

    @extend_schema_field(serializers.CharField())
    def get_type(self, obj):
        return obj.certificate.certificate.certificate_type

    @extend_schema_field(serializers.CharField())
    def get_certificate_id(self, obj):
        return obj.certificate.certificate.certificate_id


class DepotProductionSiteSerializer(serializers.ModelSerializer):
    country = PaysSerializer()
    certificates = ProductionSiteCertificateSertificate(source="productionsitecertificate_set", many=True)

    class Meta:
        model = ProductionSite
        fields = [
            "address",
            "name",
            "country",
            "id",
            "date_mise_en_service",
            "site_siret",
            "postal_code",
            "manager_name",
            "manager_phone",
            "manager_email",
            "ges_option",
            "eligible_dc",
            "dc_reference",
            "dc_number",
            "city",
            "certificates",
        ]


class EntitySiteSerializer(serializers.Serializer):
    ownership_type = serializers.ChoiceField(choices=EntitySite.TYPE_OWNERSHIP, required=True)
    blending_is_outsourced = serializers.BooleanField()
    blender = EntityUserEntitySerializer()
    depot = serializers.SerializerMethodField(allow_null=True)
    site = serializers.SerializerMethodField(allow_null=True)

    @extend_schema_field(EntityDepotSerializer)
    def get_depot(self, instance):
        if instance.site.is_depot():
            return EntityDepotSerializer(instance.site).data
        return None

    @extend_schema_field(DepotProductionSiteSerializer)
    def get_site(self, instance):
        if not instance.site.is_depot():
            return DepotProductionSiteSerializer(instance.site).data
        return None
