from math import e
from rest_framework import serializers
from doublecount.serializers import EntitySerializer

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
        return obj.production_site.name if obj.production_site else "-"

    def get_producer(self, obj):
        return obj.production_site.producer.name if obj.production_site else obj.certificate_holder
