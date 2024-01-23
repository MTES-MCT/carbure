from rest_framework import serializers
from core.serializers import EntityPreviewSerializer
from elec.models import ElecChargePointApplication


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
