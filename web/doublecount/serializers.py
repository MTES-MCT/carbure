from rest_framework import serializers
from .models import DoubleCountingAgreement, DoubleCountingProduction, DoubleCountingSourcing, DoubleCountingDocFile
from core.models import Entity, MatierePremiere, Biocarburant, Pays

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'name', 'entity_type']

class FeedStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatierePremiere
        fields = ['name', 'name_en', 'code']

class BiofuelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biocarburant
        fields = ['name', 'name_en', 'code']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pays
        fields = ['name', 'name_en', 'code_pays']


class DoubleCountingProductionSerializer(serializers.ModelSerializer):
    biofuel = BiofuelSerializer(read_only=True)
    feedstock = FeedStockSerializer(read_only=True)
    class Meta:
        model = DoubleCountingProduction
        fields = ['id', 'year', 'biofuel', 'feedstock', 'max_production_capacity', 'estimated_production', 'requested_quota', 'approved_quota']


class DoubleCountingSourcingSerializer(serializers.ModelSerializer):
    feedstock = FeedStockSerializer(read_only=True)
    origin_country = CountrySerializer(read_only=True)
    supply_country = CountrySerializer(read_only=True)
    transit_country = CountrySerializer(read_only=True)

    class Meta:
        model = DoubleCountingSourcing
        fields = ['id', 'year', 'feedstock', 'origin_country', 'supply_country', 'transit_country', 'metric_tonnes']


class DoubleCountingAgreementFullSerializer(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    producer = EntitySerializer(read_only=True)

    class Meta:
        model = DoubleCountingAgreement
        fields = ['id', 'producer', 'production_site', 'period_start', 'period_end', 'status', 'dgec_validated', 'dgec_validator', 'dgec_validated_dt', 'dgddi_validated', 'dgddi_validator', 'dgddi_validated_dt', 'dgpe_validated', 'dgpe_validator', 'dgpe_validated_dt']

class DoubleCountingDocFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoubleCountingDocFile
        fields = ['id', 'file_name']

class DoubleCountingAgreementFullSerializerWithForeignKeys(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    sourcing = DoubleCountingSourcingSerializer(many=True, read_only=True)
    production = DoubleCountingProductionSerializer(many=True, read_only=True)
    producer = EntitySerializer(read_only=True)
    documents = DoubleCountingDocFileSerializer(many=True, read_only=True)

    class Meta:
        model = DoubleCountingAgreement
        fields = ['id', 'producer', 'production_site', 'period_start', 'period_end', 'status', 'dgec_validated', 'dgec_validator', 'dgec_validated_dt', 'dgddi_validated', 'dgddi_validator', 'dgddi_validated_dt', 'dgpe_validated', 'dgpe_validator', 'dgpe_validated_dt', 'sourcing', 'production', 'documents']

class DoubleCountingAgreementPartialSerializer(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = DoubleCountingAgreement
        fields = ['id', 'producer', 'production_site', 'period_start', 'period_end', 'status']

class DoubleCountingAgreementPartialSerializerWithForeignKeys(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    producer = EntitySerializer(read_only=True)
    production = DoubleCountingProductionSerializer(many=True, read_only=True)
    sourcing = DoubleCountingSourcingSerializer(many=True, read_only=True)
    documents = DoubleCountingDocFileSerializer(many=True, read_only=True)

    class Meta:
        model = DoubleCountingAgreement
        fields = ['id', 'producer', 'production_site', 'period_start', 'period_end', 'status', 'production', 'sourcing', 'documents']

