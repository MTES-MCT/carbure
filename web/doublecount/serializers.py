from django.db.models.aggregates import Count, Sum
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from certificates.models import ProductionSiteCertificate
from core import private_storage
from core.models import MatierePremiere
from core.serializers import (
    BiofuelSerializer,
    CountrySerializer,
    EntitySerializer,
    EntitySummarySerializer,
    FeedStockSerializer,
    GenericCertificateSerializer,
)
from producers.models import ProductionSiteInput, ProductionSiteOutput
from transactions.models import ProductionSite

from .models import (
    DoubleCountingApplication,
    DoubleCountingDocFile,
    DoubleCountingProduction,
    DoubleCountingProductionHistory,
    DoubleCountingSourcing,
    DoubleCountingSourcingHistory,
)


class DoubleCountingProductionSitePreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionSite
        fields = [
            "id",
            "name",
        ]


class DoubleCountingProductionSiteSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    inputs = serializers.SerializerMethodField()
    outputs = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    producer = EntitySerializer(read_only=True)

    class Meta:
        model = ProductionSite
        fields = [
            "id",
            "producer",
            "name",
            "country",
            "date_mise_en_service",
            "ges_option",
            "eligible_dc",
            "dc_reference",
            "site_siret",
            "address",
            "city",
            "postal_code",
            "gps_coordinates",
            "manager_name",
            "manager_phone",
            "manager_email",
            "inputs",
            "outputs",
            "certificates",
        ]

    @extend_schema_field(GenericCertificateSerializer(many=True))
    def get_certificates(self, obj):
        ps_certificates = ProductionSiteCertificate.objects.filter(production_site=obj)
        certificates = [ps_certificate.certificate.certificate for ps_certificate in ps_certificates]
        return GenericCertificateSerializer(certificates, many=True).data

    @extend_schema_field(FeedStockSerializer(many=True))
    def get_inputs(self, obj):
        inputs = ProductionSiteInput.objects.filter(production_site=obj)
        feedstocks = [input.matiere_premiere for input in inputs]
        return FeedStockSerializer(feedstocks, many=True).data

    @extend_schema_field(BiofuelSerializer(many=True))
    def get_outputs(self, obj):
        inputs = ProductionSiteOutput.objects.filter(production_site=obj)
        biofuels = [input.biocarburant for input in inputs]
        return BiofuelSerializer(biofuels, many=True).data


class DoubleCountingProductionSerializer(serializers.ModelSerializer):
    biofuel = BiofuelSerializer(read_only=True)
    feedstock = FeedStockSerializer(read_only=True)

    class Meta:
        model = DoubleCountingProduction
        fields = [
            "id",
            "year",
            "biofuel",
            "feedstock",
            "max_production_capacity",
            "estimated_production",
            "requested_quota",
            "approved_quota",
        ]
        read_only_fields = fields


class DoubleCountingProductionHistorySerializer(serializers.ModelSerializer):
    biofuel = BiofuelSerializer(read_only=True)
    feedstock = FeedStockSerializer(read_only=True)

    class Meta:
        model = DoubleCountingProductionHistory
        fields = [
            "id",
            "year",
            "biofuel",
            "feedstock",
            "max_production_capacity",
            "effective_production",
        ]
        read_only_fields = fields


class DoubleCountingSourcingSerializer(serializers.ModelSerializer):
    feedstock = FeedStockSerializer(read_only=True)
    origin_country = CountrySerializer(read_only=True)
    supply_country = CountrySerializer(read_only=True)
    transit_country = CountrySerializer(read_only=True)

    class Meta:
        model = DoubleCountingSourcing
        fields = ["id", "year", "feedstock", "origin_country", "supply_country", "transit_country", "metric_tonnes"]
        read_only_fields = fields


class DoubleCountingSourcingHistorySerializer(serializers.ModelSerializer):
    feedstock = FeedStockSerializer(read_only=True)
    origin_country = CountrySerializer(read_only=True)
    supply_country = CountrySerializer(read_only=True)
    transit_country = CountrySerializer(read_only=True)

    class Meta:
        model = DoubleCountingSourcingHistory
        fields = [
            "id",
            "year",
            "feedstock",
            "origin_country",
            "supply_country",
            "transit_country",
            "metric_tonnes",
            "raw_material_supplier",
            "supplier_certificate_name",
            "supplier_certificate",
        ]


class DoubleCountingAggregatedSourcingSerializer(serializers.ModelSerializer):
    feedstock = FeedStockSerializer(read_only=True)
    sum = serializers.SerializerMethodField()

    def get_sum(self, queryset):
        return queryset.objects.values("year", "feedstock").annotate(sum=Sum("metric_tonnes"))

    class Meta:
        model = DoubleCountingSourcing
        fields = ["year", "feedstock", "sum"]


class DoubleCountingDocFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    @extend_schema_field(str)
    def get_url(self, obj):
        return private_storage.url(obj.url)

    class Meta:
        model = DoubleCountingDocFile
        fields = ["id", "file_name", "file_type", "url"]


class DoubleCountingApplicationSerializer(serializers.ModelSerializer):
    production_site = DoubleCountingProductionSiteSerializer(read_only=True)
    producer_user = serializers.SlugRelatedField(read_only=True, slug_field="email")
    sourcing = DoubleCountingSourcingSerializer(many=True, read_only=True)
    production = DoubleCountingProductionSerializer(many=True, read_only=True)
    producer = EntitySerializer(read_only=True)
    documents = DoubleCountingDocFileSerializer(many=True, read_only=True)
    download_link = serializers.SerializerMethodField()
    has_dechets_industriels = serializers.SerializerMethodField()

    class Meta:
        model = DoubleCountingApplication
        fields = [
            "id",
            "created_at",
            "producer",
            "producer_user",
            "production_site",
            "period_start",
            "period_end",
            "status",
            "sourcing",
            "production",
            "documents",
            "download_link",
            "has_dechets_industriels",
        ]

    @extend_schema_field(str)
    def get_download_link(self, obj):
        return ""

    @extend_schema_field(bool)
    def get_has_dechets_industriels(self, obj):
        return obj.has_dechets_industriels()


class DoubleCountingApplicationPartialSerializer(serializers.ModelSerializer):
    production_site = DoubleCountingProductionSitePreviewSerializer(read_only=True)
    producer = EntitySummarySerializer(read_only=True)
    agreement_id = serializers.SerializerMethodField()
    quotas_progression = serializers.SerializerMethodField()
    producer_user = serializers.SlugRelatedField(read_only=True, slug_field="email")

    class Meta:
        model = DoubleCountingApplication
        read_only_fields = ["status"]
        fields = [
            "id",
            "created_at",
            "producer",
            "production_site",
            "period_start",
            "period_end",
            "status",
            "certificate_id",
            "agreement_id",
            "quotas_progression",
            "producer_user",
        ]

    @extend_schema_field(int)
    def get_agreement_id(self, obj):
        return None

    @extend_schema_field(float)
    def get_quotas_progression(self, obj):
        return 0.0


class DoubleCountingApplicationPartialSerializerWithForeignKeys(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(read_only=True, slug_field="name")
    producer = EntitySerializer(read_only=True)
    production = DoubleCountingProductionSerializer(many=True, read_only=True)
    sourcing = DoubleCountingSourcingSerializer(many=True, read_only=True)
    documents = DoubleCountingDocFileSerializer(many=True, read_only=True)
    aggregated_sourcing = serializers.SerializerMethodField()

    def get_aggregated_sourcing(self, dca):
        agg = dca.sourcing.all().values("year", "feedstock").annotate(sum=Sum("metric_tonnes"), count=Count("metric_tonnes"))
        feedstock_ids = {a["feedstock"] for a in agg}
        feedstocks = {f.id: f for f in MatierePremiere.objects.filter(id__in=feedstock_ids)}
        for a in agg:
            s = FeedStockSerializer(feedstocks[a["feedstock"]])
            a["feedstock"] = s.data
        return list(agg)

    class Meta:
        model = DoubleCountingApplication
        fields = [
            "id",
            "created_at",
            "producer",
            "production_site",
            "period_start",
            "period_end",
            "status",
            "production",
            "sourcing",
            "aggregated_sourcing",
            "documents",
        ]
