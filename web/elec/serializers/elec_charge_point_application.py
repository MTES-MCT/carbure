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
            "charging_point_count",
            "power_total",
        ]

    cpo = EntityPreviewSerializer(read_only=True)
    application_date = serializers.DateTimeField(source="created_at")
    station_count = serializers.SerializerMethodField()
    charging_point_count = serializers.SerializerMethodField()
    power_total = serializers.SerializerMethodField()

    def get_station_count(self, instance):
        return instance.station_count

    def get_charging_point_count(self, instance):
        return instance.charging_point_count

    def get_power_total(self, instance):
        return instance.power_total
