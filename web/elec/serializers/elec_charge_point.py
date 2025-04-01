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
            "application_date",
            "installation_date",
            "mid_id",
            "measure_date",
            "measure_energy",
            "latest_meter_reading_date",
            "is_article_2",
            "measure_reference_point_id",
            "station_name",
            "station_id",
            "nominal_power",
            "cpo_name",
            "cpo_siren",
            "status",
            "latitude",
            "longitude",
            "initial_index",
            "initial_index_date",
        ]

    cpo = serializers.SlugRelatedField(read_only=True, slug_field="name")
    application_date = serializers.DateField(source="application.created_at")
    measure_energy = serializers.SerializerMethodField()
    latest_meter_reading_date = serializers.SerializerMethodField()
    nominal_power = serializers.SerializerMethodField()
    status = serializers.CharField(source="application.status", read_only=True)

    def get_measure_energy(self, instance):
        return round(instance.measure_energy or 0, 3)

    def get_latest_meter_reading_date(self, instance):
        if instance.latest_meter_reading_date:
            month = str(instance.latest_meter_reading_date.month)
            year = instance.latest_meter_reading_date.year
            return f"{month.zfill(2)}/{year}"

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
            "nominal_power",
        ]


class ElecChargePointUpdateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=ElecChargePoint.objects.filter(is_deleted=False), required=True)
    initial_index = serializers.FloatField(required=False)

    class Meta:
        model = ElecChargePoint
        fields = [
            "id",
            "charge_point_id",
            "measure_reference_point_id",
            "initial_index",
        ]


class ElecChargePointIdSerializer(serializers.Serializer):
    charge_point_id = serializers.PrimaryKeyRelatedField(
        queryset=ElecChargePoint.objects.filter(is_deleted=False), required=True
    )
