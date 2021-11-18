from rest_framework import serializers

from core.models import CarbureLot, CarbureLotEvent, CarbureLotComment, CarbureStock, CarbureStockTransformation, Depot, Entity, EntityDepot, GenericError
from doublecount.serializers import BiofuelSerializer, CountrySerializer, EntitySerializer, FeedStockSerializer
from producers.models import ProductionSite

class DepotSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    class Meta:
        model = Depot
        fields = ['id', 'name', 'city', 'depot_id', 'country', 'depot_type', 'address', 'postal_code', 'gps_coordinates', 'accise']

class EntityDepotSerializer(serializers.ModelSerializer):
    depot = DepotSerializer(read_only=True)
    entity = EntitySerializer(read_only=True)
    blender = EntitySerializer(read_only=True)
    class Meta:
        model = EntityDepot
        fields = ['entity', 'depot', 'ownership_type', 'blending_is_outsourced', 'blender']

class ProductionSiteSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    producer = EntitySerializer(read_only=True)
    class Meta:
        model = ProductionSite
        fields = ['id', 'producer', 'name', 'country', 'date_mise_en_service', 'ges_option', 'eligible_dc', 'dc_reference',
                  'site_id', 'address', 'city', 'postal_code', 'gps_coordinates', 'manager_name', 'manager_phone', 'manager_email']

class GenericErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericError
        fields = ['error', 'is_blocking', 'field', 'value', 'extra', 'fields']

class CarbureLotEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbureLotEvent
        fields = ['user', 'event_type', 'event_dt', 'metadata']

class CarbureLotCommentSerializer(serializers.ModelSerializer):
    entity=EntitySerializer(read_only=True)
    class Meta:
        model = CarbureLotComment
        fields = ['entity', 'user', 'comment_type', 'comment_dt', 'comment']

class CarbureLotCSVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbureLot
        fields = ['year', 'period', 'carbure_id', 'producer', 'production_site',
                  'production_country', 'production_site_commissioning_date', 'production_site_certificate', 'production_site_double_counting_certificate',
                  'supplier', 'supplier_certificate',
                  'transport_document_reference', 'client', 'delivery_date', 'delivery_site', 'delivery_site_country', 'delivery_type',
                  'volume', 'weight', 'lhv_amount', 'feedstock', 'biofuel', 'country_of_origin',
                  'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'ghg_reference_red_ii', 'ghg_reduction_red_ii',
                  'free_field'
                  ]

    def get_producer(self, obj):
        return obj.carbure_producer.name if obj.carbure_producer else obj.unknown_producer

    def get_production_site(self, obj):
        return obj.carbure_production_site.name if obj.carbure_production_site else obj.unknown_production_site

    def get_production_country(self, obj):
        return obj.production_country.code_pays if obj.production_country else ''

    def get_supplier(self, obj):
        return obj.carbure_supplier.name if obj.carbure_supplier else obj.unknown_supplier

    def get_client(self, obj):
        return obj.carbure_client.name if obj.carbure_client else obj.unknown_client

    def get_delivery_date(self, obj):
        return obj.delivery_date.strftime('%d/%m/%Y') if obj.delivery_date else ''

    def get_delivery_site(self, obj):
        return obj.carbure_delivery_site.depot_id if obj.carbure_delivery_site else obj.unknown_delivery_site

    def get_delivery_site_country(self, obj):
        return obj.delivery_site_country.code_pays if obj.delivery_site_country else ''

    def get_feedstock(self, obj):
        return obj.feedstock.code if obj.feedstock else ''

    def get_biofuel(self, obj):
        return obj.biofuel.code if obj.biofuel else ''

    def get_country_of_origin(self, obj):
        return obj.country_of_origin.code_pays if obj.country_of_origin else ''


class CarbureStockCSVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbureStock
        fields = ['year', 'period', 'carbure_id', 'producer', 'production_site',
                  'production_country', 'production_site_commissioning_date', 'production_site_certificate', 'production_site_double_counting_certificate',
                  'supplier', 'supplier_certificate',
                  'transport_document_reference', 'client', 'delivery_date', 'delivery_site', 'delivery_site_country', 'delivery_type',
                  'volume', 'weight', 'lhv_amount', 'feedstock', 'biofuel', 'country_of_origin',
                  'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'ghg_reference_red_ii', 'ghg_reduction_red_ii',
                  'free_field'
                  ]

    def get_producer(self, obj):
        return obj.carbure_producer.name if obj.carbure_producer else obj.unknown_producer

    def get_production_site(self, obj):
        return obj.carbure_production_site.name if obj.carbure_production_site else obj.unknown_production_site

    def get_production_country(self, obj):
        return obj.production_country.code_pays if obj.production_country else ''

    def get_supplier(self, obj):
        return obj.carbure_supplier.name if obj.carbure_supplier else obj.unknown_supplier

    def get_client(self, obj):
        return obj.carbure_client.name if obj.carbure_client else obj.unknown_client

    def get_delivery_date(self, obj):
        return obj.delivery_date.strftime('%d/%m/%Y') if obj.delivery_date else ''

    def get_delivery_site(self, obj):
        return obj.carbure_delivery_site.depot_id if obj.carbure_delivery_site else obj.unknown_delivery_site

    def get_delivery_site_country(self, obj):
        return obj.delivery_site_country.code_pays if obj.delivery_site_country else ''

    def get_feedstock(self, obj):
        return obj.feedstock.code if obj.feedstock else ''

    def get_biofuel(self, obj):
        return obj.biofuel.code if obj.biofuel else ''

    def get_country_of_origin(self, obj):
        return obj.country_of_origin.code_pays if obj.country_of_origin else ''


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
    delivery_date = serializers.SerializerMethodField()
    #parent_lot = CarbureLotPublicSerializer(read_only=True)
    parent_lot = None # defined later

    class Meta:
        model = CarbureStock
        fields = ['id', 'parent_lot', 'parent_transformation', 'carbure_id', 'depot', 'carbure_client',
                  'remaining_volume', 'remaining_weight', 'remaining_lhv_amount', 'feedstock', 'biofuel', 'country_of_origin',
                  'carbure_production_site', 'unknown_production_site', 'production_country', 'carbure_supplier', 'unknown_supplier',
                  'ghg_reduction', 'ghg_reduction_red_ii', 'initial_volume', 'delivery_date']

    def get_initial_volume(self, obj):
        return obj.parent_lot.volume if obj.parent_lot else obj.parent_transformation.volume_destination

    def get_delivery_date(self, obj):
        return obj.parent_lot.delivery_date if obj.parent_lot else obj.parent_transformation.transformation_dt

class CarbureLotPublicSerializer(serializers.ModelSerializer):
    carbure_producer = EntitySerializer(read_only=True)
    carbure_production_site = ProductionSiteSerializer(read_only=True)
    production_country = CountrySerializer(read_only=True)
    carbure_supplier = EntitySerializer(read_only=True)
    carbure_client = EntitySerializer(read_only=True)
    carbure_dispatch_site = DepotSerializer(read_only=True)
    dispatch_site_country = CountrySerializer(read_only=True)
    carbure_delivery_site = DepotSerializer(read_only=True)
    delivery_site_country = CountrySerializer(read_only=True)
    feedstock = FeedStockSerializer(read_only=True)
    biofuel = BiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    parent_stock = CarbureStockPublicSerializer(read_only=True)
    added_by = EntitySerializer(read_only=True)

    class Meta:
        model = CarbureLot
        fields = ['id', 'year', 'period', 'carbure_id',
                  'carbure_producer', 'unknown_producer', 'carbure_production_site', 'unknown_production_site',
                  'production_country', 'production_site_commissioning_date', 'production_site_certificate', 'production_site_double_counting_certificate',
                  'carbure_supplier', 'unknown_supplier', 'supplier_certificate', 'supplier_certificate_type',
                  'transport_document_type', 'transport_document_reference', 'carbure_client', 'unknown_client',
                  'dispatch_date', 'carbure_dispatch_site', 'unknown_dispatch_site', 'dispatch_site_country',
                  'delivery_date', 'carbure_delivery_site', 'unknown_delivery_site', 'delivery_site_country', 'delivery_type',
                  'lot_status', 'correction_status', 'parent_stock',
                  'volume', 'weight', 'lhv_amount', 'feedstock', 'biofuel', 'country_of_origin',
                  'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'ghg_reference_red_ii', 'ghg_reduction_red_ii',
                  'free_field', 'added_by',
                  ]

CarbureStockPublicSerializer.parent_lot = CarbureLotPublicSerializer(read_only=True)

class CarbureLotAdminSerializer(CarbureLotPublicSerializer):
    class Meta:
        model = CarbureLot
        fields = ['year', 'period', 'carbure_id',
                  'carbure_producer', 'unknown_producer', 'carbure_production_site', 'unknown_production_site',
                  'production_country', 'production_site_commissioning_date', 'production_site_certificate', 'production_site_double_counting_certificate',
                  'carbure_supplier', 'unknown_supplier', 'supplier_certificate', 'supplier_certificate_type',
                  'transport_document_type', 'transport_document_reference', 'carbure_client', 'unknown_client',
                  'dispatch_date', 'carbure_dispatch_site', 'unknown_dispatch_site', 'dispatch_site_country',
                  'delivery_date', 'carbure_delivery_site', 'unknown_delivery_site', 'delivery_site_country', 'delivery_type',
                  'lot_status', 'correction_status', 'parent_stock',
                  'volume', 'weight', 'lhv_amount', 'feedstock', 'biofuel', 'country_of_origin',
                  'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'ghg_total', 'ghg_reference', 'ghg_reduction', 'ghg_reference_red_ii', 'ghg_reduction_red_ii',
                  'free_field', 'added_by', 'highlighted_by_auditor', 'highlighted_by_admin'
                  ]