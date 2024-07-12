from rest_framework import serializers
from core.serializers import EntityPreviewSerializer
from elec.models.elec_audit_sample import ElecAuditSample
from elec.models.elec_charge_point import ElecChargePoint
from elec.serializers.elec_charge_point import ElecChargePointSampleSerializer


class ElecAuditSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecAuditSample
        fields = [
            "id",
            "cpo",
            "station_count",
            "charge_point_count",
            "application_date",
            "audit_order_date",
            "status",
        ]

    cpo = EntityPreviewSerializer()
    audit_order_date = serializers.DateField(source="created_at")
    charge_point_count = serializers.SerializerMethodField()
    station_count = serializers.SerializerMethodField()
    application_date = serializers.SerializerMethodField()
    # status = serializers.SerializerMethodField()

    def get_charge_point_count(self, instance):
        return instance.charge_point_count or 0

    def get_station_count(self, instance):
        return instance.station_count or 0

    def get_application_date(self, instance):
        if instance.charge_point_application:
            return instance.charge_point_application.created_at
        elif instance.meter_reading_application:
            return instance.meter_reading_application.created_at

    # def get_status(self, instance):
    #     if instance.charge_point_application:
    #         return instance.charge_point_application.status
    #     elif instance.meter_reading_application:
    #         return instance.meter_reading_application.status


class ElecAuditSampleDetailsSerializer(ElecAuditSampleSerializer):
    class Meta:
        model = ElecAuditSample
        fields = ElecAuditSampleSerializer.Meta.fields + ["sample"]

    sample = serializers.SerializerMethodField()

    def get_sample(self, instance):
        audited_charge_points = instance.audited_charge_points.all()
        charge_points = ElecChargePoint.objects.filter(charge_point_audit__in=audited_charge_points)

        return {
            "application_id": instance.id,
            "percentage": instance.percentage,
            "charge_points": ElecChargePointSampleSerializer(charge_points, many=True).data,
        }
