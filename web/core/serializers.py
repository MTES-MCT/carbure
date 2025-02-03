from rest_framework import serializers

from core.models import (
    CarbureLot,
    CarbureLotComment,
    CarbureLotEvent,
    CarbureLotReliabilityScore,
    CarbureNotification,
    CarbureStock,
    CarbureStockTransformation,
    Entity,
    EntityCertificate,
    EntityDepot,
    GenericCertificate,
    GenericError,
    SustainabilityDeclaration,
)
from doublecount.serializers import (
    BiofuelSerializer,
    CountrySerializer,
    EntitySerializer,
    EntitySummarySerializer,
    FeedStockSerializer,
)
from transactions.models import Airport, Depot, ProductionSite


class AirportSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Airport
        fields = [
            "id",
            "name",
            "city",
            "icao_code",
            "country",
            "site_type",
            "address",
            "postal_code",
            "gps_coordinates",
        ]


class DepotSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Depot
        fields = [
            "id",
            "name",
            "city",
            "customs_id",
            "country",
            "site_type",
            "address",
            "postal_code",
            "gps_coordinates",
            "accise",
            "electrical_efficiency",
            "thermal_efficiency",
            "useful_temperature",
        ]


class EntityDepotSerializer(serializers.ModelSerializer):
    depot = DepotSerializer(read_only=True)
    entity = EntitySerializer(read_only=True)
    blender = EntitySerializer(read_only=True)

    class Meta:
        model = EntityDepot
        fields = [
            "entity",
            "depot",
            "ownership_type",
            "blending_is_outsourced",
            "blender",
        ]


class ProductionSiteSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
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
        ]


class GenericErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericError
        fields = [
            "error",
            "is_blocking",
            "field",
            "value",
            "extra",
            "fields",
            "acked_by_creator",
            "acked_by_recipient",
        ]


class GenericErrorAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericError
        fields = [
            "error",
            "is_blocking",
            "field",
            "value",
            "extra",
            "fields",
            "acked_by_admin",
            "acked_by_auditor",
        ]


class CarbureLotEventSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        visible_users = self.context.get("visible_users")
        if visible_users is None or obj.user is None:
            return "******"
        elif obj.user.email not in visible_users:
            return "******"
        else:
            return obj.user.email

    class Meta:
        model = CarbureLotEvent
        fields = ["user", "event_type", "event_dt", "metadata"]


class CarbureLotAdminEventSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True, slug_field="email")

    class Meta:
        model = CarbureLotEvent
        fields = ["user", "event_type", "event_dt", "metadata"]


class CarbureStockEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbureLotEvent
        fields = ["user", "event_type", "event_dt", "metadata"]


class CarbureLotCommentSerializer(serializers.ModelSerializer):
    entity = EntitySerializer(read_only=True)

    class Meta:
        model = CarbureLotComment
        fields = ["entity", "user", "comment_type", "comment_dt", "comment"]


class CarbureLotCSVSerializer(serializers.ModelSerializer):
    producer = serializers.SerializerMethodField()
    production_site = serializers.SerializerMethodField()
    production_country = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    delivery_date = serializers.SerializerMethodField()
    delivery_site = serializers.SerializerMethodField()
    delivery_site_country = serializers.SerializerMethodField()
    delivery_site_name = serializers.SerializerMethodField()
    country_of_origin = serializers.SerializerMethodField()
    biofuel = serializers.SerializerMethodField()
    feedstock = serializers.SerializerMethodField()
    feedstock_category = serializers.SerializerMethodField()
    production_site_double_counting_certificate = serializers.SerializerMethodField()

    class Meta:
        model = CarbureLot
        fields = [
            "year",
            "period",
            "carbure_id",
            "producer",
            "production_site",
            "production_country",
            "production_site_commissioning_date",
            "production_site_certificate",
            "production_site_double_counting_certificate",
            "supplier",
            "supplier_certificate",
            "transport_document_reference",
            "client",
            "delivery_date",
            "delivery_site",
            "delivery_site_country",
            "delivery_type",
            "volume",
            "weight",
            "lhv_amount",
            "feedstock",
            "feedstock_category",
            "biofuel",
            "country_of_origin",
            "eec",
            "el",
            "ep",
            "etd",
            "eu",
            "esca",
            "eccs",
            "eccr",
            "eee",
            "ghg_total",
            "ghg_reference",
            "ghg_reduction",
            "ghg_reference_red_ii",
            "ghg_reduction_red_ii",
            "free_field",
            "data_reliability_score",
            "delivery_site_name",
        ]

    def get_production_site_double_counting_certificate(self, obj):
        return obj.production_site_double_counting_certificate if obj.feedstock and obj.feedstock.is_double_compte else ""

    def get_producer(self, obj):
        return obj.carbure_producer.name if obj.carbure_producer else obj.unknown_producer

    def get_production_site(self, obj):
        return obj.carbure_production_site.name if obj.carbure_production_site else obj.unknown_production_site

    def get_production_country(self, obj):
        return obj.production_country.code_pays if obj.production_country else ""

    def get_supplier(self, obj):
        return obj.carbure_supplier.name if obj.carbure_supplier else obj.unknown_supplier

    def get_client(self, obj):
        return obj.carbure_client.name if obj.carbure_client else obj.unknown_client

    def get_delivery_date(self, obj):
        return obj.delivery_date.strftime("%d/%m/%Y") if obj.delivery_date else ""

    def get_delivery_site(self, obj):
        return obj.carbure_delivery_site.depot_id if obj.carbure_delivery_site else obj.unknown_delivery_site

    def get_delivery_site_country(self, obj):
        return obj.delivery_site_country.code_pays if obj.delivery_site_country else ""

    def get_delivery_site_name(self, obj):
        return obj.carbure_delivery_site.name if obj.carbure_delivery_site else obj.unknown_delivery_site

    def get_feedstock(self, obj):
        return obj.feedstock.code if obj.feedstock else ""

    def get_feedstock_category(self, obj):
        return obj.feedstock.category if obj.feedstock else ""

    def get_biofuel(self, obj):
        return obj.biofuel.code if obj.biofuel else ""

    def get_country_of_origin(self, obj):
        return obj.country_of_origin.code_pays if obj.country_of_origin else ""


class CarbureStockCSVSerializer(serializers.ModelSerializer):
    production_site = serializers.SerializerMethodField()
    production_country = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    delivery_date = serializers.SerializerMethodField()
    depot = serializers.SerializerMethodField()
    depot_name = serializers.SerializerMethodField()
    feedstock = serializers.SerializerMethodField()
    biofuel = serializers.SerializerMethodField()
    country_of_origin = serializers.SerializerMethodField()

    class Meta:
        model = CarbureStock
        fields = [
            "carbure_id",
            "production_site",
            "production_country",
            "supplier",
            "delivery_date",
            "depot",
            "depot_name",
            "remaining_volume",
            "remaining_weight",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "ghg_reduction_red_ii",
        ]

    def get_production_site(self, obj):
        return obj.carbure_production_site.name if obj.carbure_production_site else obj.unknown_production_site

    def get_production_country(self, obj):
        return obj.production_country.code_pays if obj.production_country else ""

    def get_supplier(self, obj):
        return obj.carbure_supplier.name if obj.carbure_supplier else obj.unknown_supplier

    def get_delivery_date(self, obj):
        date = obj.get_delivery_date()
        return date.strftime("%d/%m/%Y") if date else ""

    def get_depot(self, obj):
        return obj.depot.depot_id if obj.depot else ""

    def get_depot_name(self, obj):
        return obj.depot.name if obj.depot else ""

    def get_feedstock(self, obj):
        return obj.feedstock.code if obj.feedstock else ""

    def get_biofuel(self, obj):
        return obj.biofuel.code if obj.biofuel else ""

    def get_country_of_origin(self, obj):
        return obj.country_of_origin.code_pays if obj.country_of_origin else ""


class CarbureStockPublicSerializer(serializers.ModelSerializer):
    depot = DepotSerializer(read_only=True)
    carbure_client = EntitySerializer(read_only=True)
    feedstock = FeedStockSerializer(read_only=True)
    biofuel = BiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    carbure_production_site = ProductionSiteSerializer(read_only=True)
    production_country = CountrySerializer(read_only=True)
    carbure_supplier = EntitySerializer(read_only=True)
    initial_volume = serializers.SerializerMethodField()
    initial_weight = serializers.SerializerMethodField()
    initial_lhv_amount = serializers.SerializerMethodField()
    delivery_date = serializers.SerializerMethodField()
    period = serializers.SerializerMethodField()

    class Meta:
        model = CarbureStock
        fields = [
            "id",
            "carbure_id",
            "depot",
            "carbure_client",
            "remaining_volume",
            "remaining_weight",
            "remaining_lhv_amount",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "carbure_production_site",
            "unknown_production_site",
            "production_country",
            "carbure_supplier",
            "unknown_supplier",
            "ghg_reduction",
            "ghg_reduction_red_ii",
            "initial_volume",
            "delivery_date",
            "period",
            "initial_weight",
            "initial_lhv_amount",
        ]

    def get_initial_volume(self, obj):
        if obj.parent_lot:
            return obj.parent_lot.volume
        elif obj.parent_transformation:
            return obj.parent_transformation.volume_destination
        else:
            return 0

    def get_initial_weight(self, obj):
        if obj.parent_lot:
            return obj.parent_lot.weight
        elif obj.parent_transformation:
            return obj.parent_transformation.get_weight()
        else:
            return 0

    def get_initial_lhv_amount(self, obj):
        if obj.parent_lot:
            return obj.parent_lot.lhv_amount
        elif obj.parent_transformation:
            return obj.parent_transformation.get_lhv_amount()
        else:
            return 0

    def get_delivery_date(self, obj):
        return obj.get_delivery_date().strftime("%Y-%m-%d")

    def get_period(self, obj):
        date = obj.get_delivery_date()
        return date.year * 100 + date.month


class CarbureStockTransformationPublicSerializer(serializers.ModelSerializer):
    source_stock = CarbureStockPublicSerializer(read_only=True)
    dest_stock = CarbureStockPublicSerializer(read_only=True)

    class Meta:
        model = CarbureStockTransformation
        fields = [
            "transformation_type",
            "source_stock",
            "dest_stock",
            "volume_deducted_from_source",
            "volume_destination",
            "metadata",
            "transformed_by",
            "entity",
            "transformation_dt",
        ]


class CarbureLotPublicSerializer(serializers.ModelSerializer):
    carbure_producer = EntitySummarySerializer(read_only=True)
    carbure_production_site = ProductionSiteSerializer(read_only=True)
    production_country = CountrySerializer(read_only=True)
    carbure_supplier = EntitySummarySerializer(read_only=True)
    carbure_client = EntitySummarySerializer(read_only=True)
    carbure_dispatch_site = DepotSerializer(read_only=True)
    dispatch_site_country = CountrySerializer(read_only=True)
    carbure_delivery_site = DepotSerializer(read_only=True)
    delivery_site_country = CountrySerializer(read_only=True)
    feedstock = FeedStockSerializer(read_only=True)
    biofuel = BiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    added_by = EntitySummarySerializer(read_only=True)
    carbure_vendor = EntitySummarySerializer(read_only=True)

    class Meta:
        model = CarbureLot
        fields = [
            "id",
            "year",
            "period",
            "carbure_id",
            "carbure_producer",
            "unknown_producer",
            "carbure_production_site",
            "unknown_production_site",
            "production_country",
            "production_site_commissioning_date",
            "production_site_certificate",
            "production_site_double_counting_certificate",
            "carbure_supplier",
            "unknown_supplier",
            "supplier_certificate",
            "supplier_certificate_type",
            "transport_document_type",
            "transport_document_reference",
            "carbure_client",
            "unknown_client",
            "dispatch_date",
            "carbure_dispatch_site",
            "unknown_dispatch_site",
            "dispatch_site_country",
            "delivery_date",
            "carbure_delivery_site",
            "unknown_delivery_site",
            "delivery_site_country",
            "delivery_type",
            "lot_status",
            "correction_status",
            "volume",
            "weight",
            "lhv_amount",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "eec",
            "el",
            "ep",
            "etd",
            "eu",
            "esca",
            "eccs",
            "eccr",
            "eee",
            "ghg_total",
            "ghg_reference",
            "ghg_reduction",
            "ghg_reference_red_ii",
            "ghg_reduction_red_ii",
            "free_field",
            "added_by",
            "created_at",
            "carbure_vendor",
            "vendor_certificate",
            "vendor_certificate_type",
            "data_reliability_score",
        ]


class CarbureLotAdminSerializer(CarbureLotPublicSerializer):
    class Meta:
        model = CarbureLot
        fields = [
            "id",
            "year",
            "period",
            "carbure_id",
            "carbure_producer",
            "unknown_producer",
            "carbure_production_site",
            "unknown_production_site",
            "production_country",
            "production_site_commissioning_date",
            "production_site_certificate",
            "production_site_double_counting_certificate",
            "carbure_supplier",
            "unknown_supplier",
            "supplier_certificate",
            "supplier_certificate_type",
            "transport_document_type",
            "transport_document_reference",
            "carbure_client",
            "unknown_client",
            "dispatch_date",
            "carbure_dispatch_site",
            "unknown_dispatch_site",
            "dispatch_site_country",
            "delivery_date",
            "carbure_delivery_site",
            "unknown_delivery_site",
            "delivery_site_country",
            "delivery_type",
            "lot_status",
            "correction_status",
            "audit_status",
            "volume",
            "weight",
            "lhv_amount",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "eec",
            "el",
            "ep",
            "etd",
            "eu",
            "esca",
            "eccs",
            "eccr",
            "eee",
            "ghg_total",
            "ghg_reference",
            "ghg_reduction",
            "ghg_reference_red_ii",
            "ghg_reduction_red_ii",
            "free_field",
            "added_by",
            "created_at",
            "highlighted_by_auditor",
            "highlighted_by_admin",
            "carbure_vendor",
            "vendor_certificate",
            "vendor_certificate_type",
            "data_reliability_score",
        ]


class CarbureLotPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbureLot
        fields = ["id", "carbure_id", "volume", "delivery_date"]


class CarbureLotReliabilityScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbureLotReliabilityScore
        fields = ["item", "max_score", "score", "meta"]


class GenericCertificateSerializer(serializers.ModelSerializer):
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


class EntityCertificateSerializer(serializers.ModelSerializer):
    entity = EntitySerializer()
    certificate = GenericCertificateSerializer()

    class Meta:
        model = EntityCertificate
        fields = [
            "id",
            "entity",
            "certificate",
            "has_been_updated",
            "checked_by_admin",
            "rejected_by_admin",
            "added_dt",
        ]


class SustainabilityDeclarationSerializer(serializers.ModelSerializer):
    entity = EntitySerializer()
    period = serializers.SerializerMethodField()

    def get_period(self, obj):
        return obj.period.year * 100 + obj.period.month

    class Meta:
        model = SustainabilityDeclaration
        fields = [
            "entity",
            "declared",
            "checked",
            "deadline",
            "period",
            "reminder_count",
        ]


class CarbureNotificationSerializer(serializers.ModelSerializer):
    dest = EntitySerializer()

    class Meta:
        model = CarbureNotification
        fields = [
            "id",
            "dest",
            "datetime",
            "type",
            "acked",
            "send_by_email",
            "email_sent",
            "meta",
        ]


class EntityPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ["id", "name", "entity_type"]
        read_only_fields = fields
