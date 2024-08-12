from rest_framework import serializers
from core.serializers import EntityPreviewSerializer
from elec.models import ElecChargePointApplication
from django.contrib.auth import get_user_model

from elec.models.elec_charge_point import ElecChargePoint
from elec.serializers.elec_charge_point import ElecChargePointSampleSerializer


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
    application_date = serializers.DateField(source="created_at")
    station_count = serializers.SerializerMethodField()
    charge_point_count = serializers.SerializerMethodField()
    power_total = serializers.SerializerMethodField()

    def get_station_count(self, instance):
        return instance.station_count

    def get_charge_point_count(self, instance):
        return instance.charge_point_count

    def get_power_total(self, instance):
        return round(instance.power_total or 0, 3)


class ElecChargePointApplicationDetailsSerializer(ElecChargePointApplicationSerializer):
    class Meta:
        model = ElecChargePointApplication
        fields = ElecChargePointApplicationSerializer.Meta.fields + ["email_contacts", "sample"]

    email_contacts = serializers.SerializerMethodField()
    sample = serializers.SerializerMethodField()

    def get_email_contacts(self, instance):
        user_model = get_user_model()
        users = user_model.objects.filter(userrights__entity__id=instance.cpo.id, userrights__role="ADMIN")
        return [u.email for u in users]

    def get_sample(self, instance):
        audit_sample = instance.audit_sample.first()

        # old applications do not have a registered audit sample
        if not audit_sample:
            return None

        audited_charge_points = audit_sample.audited_charge_points.all()
        comment_count = audited_charge_points.exclude(comment="").count()
        auditor_name = audit_sample.auditor.name if audit_sample.auditor else None
        charge_points = ElecChargePoint.objects.filter(charge_point_audit__in=audited_charge_points)

        return {
            "application_id": instance.id,
            "percentage": audit_sample.percentage,
            "comment_count": comment_count,
            "auditor_name": auditor_name,
            "charge_points": ElecChargePointSampleSerializer(charge_points, many=True).data,
        }
