from rest_framework import serializers
from core.serializers import EntityPreviewSerializer
from elec.models import ElecMeterReadingApplication


class ElecMeterReadingApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecMeterReadingApplication
        fields = [
            "id",
            "cpo",
            "charging_point_count",
            "energy_total",
            "year",
            "quarter",
            "application_date",
            "status",
        ]

    cpo = EntityPreviewSerializer()
    application_date = serializers.DateTimeField(source="created_at")
    charging_point_count = serializers.SerializerMethodField()
    energy_total = serializers.SerializerMethodField()

    def get_charging_point_count(self, instance):
        return instance.charging_point_count

    def get_energy_total(self, instance):
        return round(instance.energy_total, 2)
