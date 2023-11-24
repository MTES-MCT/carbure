from rest_framework import serializers
from core.serializers import EntityPreviewSerializer
from elec.models import ElecChargePoint


class ElecChargePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecChargePoint
        fields = [
            "id",
            "cpo",
            "charge_point_id",
            "current_type",
            "installation_date",
            "lne_certificate",
            "meter_reading_date",
            "meter_reading_energy",
            "is_using_reference_meter",
            "is_auto_consumption",
            "has_article_4_regularization",
            "reference_meter_id",
            "station_name",
            "station_id",
        ]

    cpo = serializers.SlugRelatedField(read_only=True, slug_field="name")
    meter_reading_energy = serializers.SerializerMethodField()

    def get_meter_reading_energy(self, instance):
        return round(instance.meter_reading_energy, 2)
