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
            "mid_id",
            "measure_date",
            "measure_energy",
            "is_article_2",
            "is_auto_consumption",
            "is_article_4",
            "measure_reference_point_id",
            "station_name",
            "station_id",
            "nominal_power",
        ]

    cpo = serializers.SlugRelatedField(read_only=True, slug_field="name")
    measure_energy = serializers.SerializerMethodField()

    def get_measure_energy(self, instance):
        return round(instance.measure_energy, 2)
