from rest_framework import serializers

from core.models import CarbureLot, CarbureLotEvent, CarbureLotComment, CarbureStock, CarbureStockTransformation

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

