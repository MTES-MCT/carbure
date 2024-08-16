from rest_framework import serializers
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
            "measure_reference_point_id",
            "station_name",
            "station_id",
            "nominal_power",
            "cpo_name",
            "cpo_siren",
            "status",
        ]

    cpo = serializers.SlugRelatedField(read_only=True, slug_field="name")
    measure_energy = serializers.SerializerMethodField()
    nominal_power = serializers.SerializerMethodField()
    status = serializers.CharField(source="application.status", read_only=True)

    def get_measure_energy(self, instance):
        return round(instance.measure_energy or 0, 3)

    def get_nominal_power(self, instance):
        return round(instance.nominal_power or 0, 3)


class ElecChargePointSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecChargePoint
        fields = [
            "id",
            "latitude",
            "longitude",
            "station_id",
            "charge_point_id",
            "mid_id",
            "measure_reference_point_id",
            "is_article_2",
        ]


class ElecChargePointUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ElecChargePoint
        fields = [
            "id",
            "charge_point_id",
        ]


class ElecChargePointIdSerializer(serializers.Serializer):
    charge_point_id = serializers.PrimaryKeyRelatedField(queryset=ElecChargePoint.objects.all(), required=True)
