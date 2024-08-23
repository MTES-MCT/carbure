from django.db.models.aggregates import Count, Sum
from rest_framework import serializers

from certificates.models import ProductionSiteCertificate
from core.models import Biocarburant, Entity, GenericCertificate, MatierePremiere, Pays
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput

from .models import DoubleCountingApplication, DoubleCountingDocFile, DoubleCountingProduction, DoubleCountingSourcing


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = [
            "id",
            "name",
            "entity_type",
            "has_mac",
            "has_trading",
            "has_direct_deliveries",
            "has_stocks",
            "preferred_unit",
            "legal_name",
            "registration_id",
            "sustainability_officer_phone_number",
            "sustainability_officer",
            "registered_address",
            "registered_zipcode",
            "registered_city",
            "registered_country",
            "activity_description",
            "website",
            "vat_number",
        ]


class EntitySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = [
            "id",
            "name",
            "entity_type",
        ]


class FeedStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatierePremiere
        fields = ["name", "name_en", "code", "category", "is_double_compte"]


class BiofuelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biocarburant
        fields = ["name", "name_en", "code"]


class ProductionSiteCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericCertificate
        fields = [
            "certificate_id",
            "certificate_type",
            "certificate_holder",
            "certificate_issuer",
            "address",
            "valid_from",
            "valid_until",
            "download_link",
            "scope",
            "input",
            "output",
        ]


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pays
        fields = ["name", "name_en", "code_pays", "is_in_europe"]


class DoubleCountingProductionSiteSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    inputs = serializers.SerializerMethodField()
    outputs = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()

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
            "site_id",
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

    def get_certificates(self, obj):
        ps_certificates = ProductionSiteCertificate.objects.filter(production_site=obj)
        certificates = [ps_certificate.certificate.certificate for ps_certificate in ps_certificates]
        return ProductionSiteCertificateSerializer(certificates, many=True).data

    def get_inputs(self, obj):
        inputs = ProductionSiteInput.objects.filter(production_site=obj)
        feedstocks = [input.matiere_premiere for input in inputs]
        return FeedStockSerializer(feedstocks, many=True).data

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


class DoubleCountingSourcingSerializer(serializers.ModelSerializer):
    feedstock = FeedStockSerializer(read_only=True)
    origin_country = CountrySerializer(read_only=True)
    supply_country = CountrySerializer(read_only=True)
    transit_country = CountrySerializer(read_only=True)

    class Meta:
        model = DoubleCountingSourcing
        fields = ["id", "year", "feedstock", "origin_country", "supply_country", "transit_country", "metric_tonnes"]


class DoubleCountingAggregatedSourcingSerializer(serializers.ModelSerializer):
    feedstock = FeedStockSerializer(read_only=True)
    sum = serializers.SerializerMethodField()

    def get_sum(self, queryset):
        return queryset.objects.values("year", "feedstock").annotate(sum=Sum("metric_tonnes"))

    class Meta:
        model = DoubleCountingSourcing
        fields = ["year", "feedstock", "sum"]


class DoubleCountingApplicationFullSerializer(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(read_only=True, slug_field="name")
    producer_user = serializers.SlugRelatedField(read_only=True, slug_field="email")
    producer = EntitySerializer(read_only=True)

    class Meta:
        model = DoubleCountingApplication
        fields = [
            "id",
            "certificate_id",
            "created_at",
            "producer",
            "producer_user",
            "production_site",
            "period_start",
            "period_end",
            "status",
        ]


class DoubleCountingDocFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoubleCountingDocFile
        fields = ["id", "file_name", "file_type"]


class DoubleCountingApplicationSerializer(serializers.ModelSerializer):
    production_site = DoubleCountingProductionSiteSerializer(read_only=True)
    producer_user = serializers.SlugRelatedField(read_only=True, slug_field="email")
    sourcing = DoubleCountingSourcingSerializer(many=True, read_only=True)
    production = DoubleCountingProductionSerializer(many=True, read_only=True)
    producer = EntitySerializer(read_only=True)
    documents = DoubleCountingDocFileSerializer(many=True, read_only=True)

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
        ]


class DoubleCountingApplicationPartialSerializer(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(read_only=True, slug_field="name")

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
            "certificate_id",
        ]


class DoubleCountingApplicationPartialSerializerWithForeignKeys(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(read_only=True, slug_field="name")
    producer = EntitySerializer(read_only=True)
    production = DoubleCountingProductionSerializer(many=True, read_only=True)
    sourcing = DoubleCountingSourcingSerializer(many=True, read_only=True)
    documents = DoubleCountingDocFileSerializer(many=True, read_only=True)
    aggregated_sourcing = serializers.SerializerMethodField()

    def get_aggregated_sourcing(self, dca):
        agg = dca.sourcing.all().values("year", "feedstock").annotate(sum=Sum("metric_tonnes"), count=Count("metric_tonnes"))
        feedstock_ids = set(list([a["feedstock"] for a in agg]))
        feedstocks = {f.id: f for f in MatierePremiere.objects.filter(id__in=feedstock_ids)}
        for a in agg:
            s = FeedStockSerializer(feedstocks[a["feedstock"]])
            a["feedstock"] = s.data
        return [a for a in agg]

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
