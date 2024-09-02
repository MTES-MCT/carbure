from rest_framework import serializers
from elec.models.elec_audit_charge_point import ElecAuditChargePoint


class ElecAuditChargePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecAuditChargePoint
        fields = [
            "charge_point_id",
            "latitude",
            "longitude",
            "is_auditable",
            "current_type",
            "observed_mid_or_prm_id",
            "observed_energy_reading",
            "has_dedicated_pdl",
            "audit_date",
            "comment",
            "station_id",
            "is_article_2",
            "measure_reference_point_id",
            "mid_id",
        ]

    is_auditable = serializers.BooleanField()
    current_type = serializers.CharField()
    observed_mid_or_prm_id = serializers.CharField()
    observed_energy_reading = serializers.FloatField()
    has_dedicated_pdl = serializers.BooleanField()
    audit_date = serializers.DateField(format="%d/%m/%Y")
    comment = serializers.CharField()
    charge_point_id = serializers.SlugRelatedField(source="charge_point", slug_field="charge_point_id", read_only=True)
    latitude = serializers.SlugRelatedField(source="charge_point", slug_field="latitude", read_only=True)
    longitude = serializers.SlugRelatedField(source="charge_point", slug_field="longitude", read_only=True)
    station_id = serializers.SlugRelatedField(source="charge_point", slug_field="station_id", read_only=True)
    is_article_2 = serializers.SlugRelatedField(source="charge_point", slug_field="is_article_2", read_only=True)
    measure_reference_point_id = serializers.SlugRelatedField(source="charge_point", slug_field="measure_reference_point_id", read_only=True)  # fmt:skip
    mid_id = serializers.SlugRelatedField(source="charge_point", slug_field="mid_id", read_only=True)
