from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.serializers import BiofuelSerializer, EntitySummarySerializer, FeedStockSerializer
from doublecount.models import DoubleCountingProduction
from doublecount.serializers import (
    BiofuelSerializer,
    CountrySerializer,
    DoubleCountingApplicationSerializer,
    EntitySummarySerializer,
    FeedStockSerializer,
)

from .models import DoubleCountingRegistration


class ProductionSiteInfoSerializer(serializers.Serializer):
    name = serializers.CharField()
    city = serializers.CharField()
    address = serializers.CharField()
    postal_code = serializers.CharField()
    country = serializers.SerializerMethodField()

    def get_country(self, obj):
        return obj.country.name if obj.country else None


class DoubleCountingRegistrationSerializer(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(read_only=True, slug_field="name")
    producer = serializers.SerializerMethodField()
    quotas_progression = serializers.SerializerMethodField()

    class Meta:
        model = DoubleCountingRegistration
        fields = [
            "id",
            "certificate_id",
            "valid_from",
            "producer",
            "production_site",
            "valid_until",
            "status",
            "quotas_progression",
        ]

    @extend_schema_field(str)
    def get_production_site(self, obj):
        return obj.production_site.name if obj.production_site else None

    @extend_schema_field(EntitySummarySerializer())
    def get_producer(self, obj):
        return EntitySummarySerializer(obj.production_site.producer).data if obj.production_site else None

    @extend_schema_field(float)
    def get_quotas_progression(self, obj):
        return 0.0


class DoubleCountingRegistrationPublicSerializer(serializers.ModelSerializer):
    production_site = ProductionSiteInfoSerializer()
    biofuel_list = serializers.SerializerMethodField()

    class Meta:
        model = DoubleCountingRegistration
        fields = [
            "production_site",
            "certificate_id",
            "valid_from",
            "valid_until",
            "biofuel_list",
        ]

    @extend_schema_field(str)
    def get_biofuel_list(self, obj: DoubleCountingRegistration):
        if not obj.application:
            biofuel_list = "NC"
        else:
            productions = DoubleCountingProduction.objects.filter(
                dca=obj.application, approved_quota__gt=0, year=obj.valid_from.year
            )
            biofuel_list = ", ".join(
                [production.biofuel.name + " (" + production.feedstock.name + ")" for production in productions]
            )
        return biofuel_list


class DoubleCountingQuotaSerializer(serializers.Serializer):
    approved_quota = serializers.IntegerField()
    biofuel = BiofuelSerializer()
    feedstock = FeedStockSerializer()
    id = serializers.IntegerField()
    lot_count = serializers.IntegerField()
    production_tonnes = serializers.IntegerField()
    quotas_progression = serializers.IntegerField()
    requested_quota = serializers.IntegerField()
    year = serializers.IntegerField()


class DoubleCountingRegistrationDetailsSerializer(serializers.ModelSerializer):
    application = DoubleCountingApplicationSerializer()
    production_site = serializers.SerializerMethodField()
    producer = serializers.SerializerMethodField()
    quotas = serializers.SerializerMethodField()

    class Meta:
        model = DoubleCountingRegistration
        fields = [
            "id",
            "certificate_id",
            "valid_from",
            "valid_until",
            "status",
            "producer",
            "production_site",
            "application",
            "quotas",
        ]

    @extend_schema_field(str)
    def get_production_site(self, obj):
        return obj.production_site.name if obj.production_site else None

    @extend_schema_field(str)
    def get_producer(self, obj):
        return obj.production_site.producer.name if obj.production_site else obj.certificate_holder

    @extend_schema_field(serializers.ListSerializer(child=DoubleCountingQuotaSerializer()))
    def get_quotas(self, obj):
        return []


class ProductionSiteResourceSerializer(serializers.Serializer):
    name = serializers.CharField()
    city = serializers.CharField()
    address = serializers.CharField()
    postal_code = serializers.CharField()
    country = CountrySerializer()
    date_mise_en_service = serializers.DateField()

    def get_country(self, obj):
        return obj.country.name if obj.country else None


class DoubleCountingRegistrationResourceSerializer(serializers.ModelSerializer):
    production_site = ProductionSiteResourceSerializer()
    producer = serializers.SerializerMethodField()

    class Meta:
        model = DoubleCountingRegistration
        fields = [
            "id",
            "certificate_id",
            "producer",
            "production_site",
        ]

    @extend_schema_field(EntitySummarySerializer())
    def get_producer(self, obj):
        return EntitySummarySerializer(obj.production_site.producer).data if obj.production_site else None
