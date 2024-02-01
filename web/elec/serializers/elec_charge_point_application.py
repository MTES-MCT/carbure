from rest_framework import serializers
from core.serializers import EntityPreviewSerializer
from elec.models import ElecChargePointApplication
from django.contrib.auth import get_user_model


class ElecChargePointApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecChargePointApplication
        fields = [
            "id",
            "cpo",
            "status",
            "application_date",
            "station_count",
            "charge_point_count",
            "power_total",
        ]

    cpo = EntityPreviewSerializer()
    application_date = serializers.DateTimeField(source="created_at")
    station_count = serializers.SerializerMethodField()
    charge_point_count = serializers.SerializerMethodField()
    power_total = serializers.SerializerMethodField()

    def get_station_count(self, instance):
        return instance.station_count

    def get_charge_point_count(self, instance):
        return instance.charge_point_count

    def get_power_total(self, instance):
        return round(instance.power_total, 2)


class ElecChargePointApplicationDetailsSerializer(ElecChargePointApplicationSerializer):
    email_contact = serializers.SerializerMethodField()

    class Meta:
        model = ElecChargePointApplication
        fields = ElecChargePointApplicationSerializer.Meta.fields + ["email_contact"]

    def get_email_contact(self, instance):
        user_model = get_user_model()
        users = user_model.objects.filter(userrights__entity__id=instance.cpo.id, userrights__role="ADMIN")
        return users.first().email if users.exists() else None
