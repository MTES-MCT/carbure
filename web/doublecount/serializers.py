from os import read
from django.db.models.aggregates import Count, Sum
from django.db.models.fields import related_descriptors
from numpy.lib.twodim_base import triu_indices_from
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from .models import DoubleCountingAgreement, DoubleCountingProduction, DoubleCountingSourcing, DoubleCountingDocFile
from core.models import Entity, MatierePremiere, Biocarburant, Pays

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'name', 'entity_type', 'has_mac', 'has_trading', 'has_direct_deliveries', 'has_stocks', 'preferred_unit',
            'legal_name', 'registration_id', 'sustainability_officer_phone_number', 'sustainability_officer', 'registered_address', 'registered_zipcode', 'registered_city', 'registered_country']

class FeedStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatierePremiere
        fields = ['name', 'name_en', 'code', 'category', 'is_double_compte']

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

class DoubleCountingAggregatedSourcingSerializer(serializers.ModelSerializer):
    feedstock = FeedStockSerializer(read_only=True)
    sum = serializers.SerializerMethodField()

    def get_sum(self, queryset):
        print(queryset)
        return queryset.objects.values('year', 'feedstock').annotate(sum=Sum('metric_tonnes'))

    class Meta:
        model = DoubleCountingSourcing
        fields = ['year', 'feedstock', 'sum']



class DoubleCountingAgreementFullSerializer(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    producer_user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='email'
    )
    dgec_validator = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    dgpe_validator = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    dgddi_validator = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    producer = EntitySerializer(read_only=True)

    class Meta:
        model = DoubleCountingAgreement
        fields = ['id', 'creation_date', 'producer', 'producer_user', 'production_site', 'period_start', 'period_end', 'status', 'dgec_validated', 'dgec_validator', 'dgec_validated_dt', 'dgddi_validated', 'dgddi_validator', 'dgddi_validated_dt', 'dgpe_validated', 'dgpe_validator', 'dgpe_validated_dt']

class DoubleCountingDocFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoubleCountingDocFile
        fields = ['id', 'file_name', 'file_type']

class DoubleCountingAgreementFullSerializerWithForeignKeys(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    producer_user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='email'
    )
    dgec_validator = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    dgpe_validator = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    dgddi_validator = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    sourcing = DoubleCountingSourcingSerializer(many=True, read_only=True)
    aggregated_sourcing = serializers.SerializerMethodField()
    production = DoubleCountingProductionSerializer(many=True, read_only=True)
    producer = EntitySerializer(read_only=True)
    documents = DoubleCountingDocFileSerializer(many=True, read_only=True)

    def get_aggregated_sourcing(self, dca):
        agg = dca.sourcing.all().values('year', 'feedstock').annotate(sum=Sum('metric_tonnes'), count=Count('metric_tonnes'))
        feedstock_ids = set(list([a['feedstock'] for a in agg]))
        feedstocks = {f.id: f for f in MatierePremiere.objects.filter(id__in=feedstock_ids)}
        for a in agg:
            s = FeedStockSerializer(feedstocks[a['feedstock']])
            a['feedstock'] = s.data
        return [a for a in agg]

    class Meta:
        model = DoubleCountingAgreement
        fields = ['id', 'creation_date', 'producer', 'producer_user', 'production_site', 'period_start', 'period_end', 'status', 'dgec_validated', 'dgec_validator', 'dgec_validated_dt', 'dgddi_validated', 'dgddi_validator', 'dgddi_validated_dt', 'dgpe_validated', 'dgpe_validator', 'dgpe_validated_dt', 'sourcing', 'aggregated_sourcing', 'production', 'documents']

class DoubleCountingAgreementPartialSerializer(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = DoubleCountingAgreement
        fields = ['id', 'creation_date', 'producer', 'production_site', 'period_start', 'period_end', 'status']

class DoubleCountingAgreementPartialSerializerWithForeignKeys(serializers.ModelSerializer):
    production_site = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    producer = EntitySerializer(read_only=True)
    production = DoubleCountingProductionSerializer(many=True, read_only=True)
    sourcing = DoubleCountingSourcingSerializer(many=True, read_only=True)
    documents = DoubleCountingDocFileSerializer(many=True, read_only=True)
    aggregated_sourcing = serializers.SerializerMethodField()

    def get_aggregated_sourcing(self, dca):
        agg = dca.sourcing.all().values('year', 'feedstock').annotate(sum=Sum('metric_tonnes'), count=Count('metric_tonnes'))
        feedstock_ids = set(list([a['feedstock'] for a in agg]))
        feedstocks = {f.id: f for f in MatierePremiere.objects.filter(id__in=feedstock_ids)}
        for a in agg:
            s = FeedStockSerializer(feedstocks[a['feedstock']])
            a['feedstock'] = s.data
        return [a for a in agg]

    class Meta:
        model = DoubleCountingAgreement
        fields = ['id', 'creation_date', 'producer', 'production_site', 'period_start', 'period_end', 'status', 'production', 'sourcing', 'aggregated_sourcing', 'documents']

