from rest_framework import serializers
from doublecount.models import DoubleCountingProduction
from doublecount.serializers import (
    DoubleCountingApplicationSerializer,
)

from .models import (
    DoubleCountingRegistration,
)


class DoubleCountingRegistrationSerializer(serializers.ModelSerializer):
    production_site = serializers.SerializerMethodField()
    producer = serializers.SerializerMethodField()

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
        ]

    def get_production_site(self, obj):
        return obj.production_site.name if obj.production_site else None

    def get_producer(self, obj):
        return obj.production_site.producer.name if obj.production_site else obj.certificate_holder


class DoubleCountingRegistrationPublicSerializer(serializers.ModelSerializer):
    production_site = serializers.SerializerMethodField()
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

    def get_production_site(self, obj: DoubleCountingRegistration):
        return {
            "name": obj.production_site.name if obj.production_site else None,
            "city": obj.production_site.city,
            "address": obj.production_site.address,
            "postal_code": obj.production_site.postal_code,
            "country": obj.production_site.country.name,
        }

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


class DoubleCountingRegistrationDetailsSerializer(serializers.ModelSerializer):
    application = DoubleCountingApplicationSerializer()
    production_site = serializers.SerializerMethodField()
    producer = serializers.SerializerMethodField()

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
        ]

    def get_production_site(self, obj):
        return obj.production_site.name if obj.production_site else None

    def get_producer(self, obj):
        return obj.production_site.producer.name if obj.production_site else obj.certificate_holder
