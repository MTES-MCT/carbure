from rest_framework import serializers
from core.serializers import EntityPreviewSerializer
from elec.models import ElecMeterReadingApplication
from django.contrib.auth import get_user_model

from elec.models.elec_charge_point import ElecChargePoint
from elec.serializers.elec_charge_point import ElecChargePointSampleSerializer


class ElecMeterReadingApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecMeterReadingApplication
        fields = [
            "id",
            "cpo",
            "charge_point_count",
            "energy_total",
            "year",
            "quarter",
            "application_date",
            "status",
        ]

    cpo = EntityPreviewSerializer()
    application_date = serializers.DateField(source="created_at")
    charge_point_count = serializers.SerializerMethodField()
    energy_total = serializers.SerializerMethodField()

    def get_charge_point_count(self, instance):
        return instance.charge_point_count

    def get_energy_total(self, instance):
        return round(instance.energy_total or 0, 3)


class ElecMeterReadingApplicationDetailsSerializer(ElecMeterReadingApplicationSerializer):
    class Meta:
        model = ElecMeterReadingApplication
        fields = ElecMeterReadingApplicationSerializer.Meta.fields + ["power_total", "email_contacts", "sample"]

    power_total = serializers.SerializerMethodField()
    email_contacts = serializers.SerializerMethodField()
    sample = serializers.SerializerMethodField()

    def get_power_total(self, instance):
        return round(instance.power_total or 0, 3)

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
        charge_points = ElecChargePoint.objects.filter(charge_point_audit__in=audited_charge_points)

        return {
            "application_id": instance.id,
            "percentage": audit_sample.percentage,
            "charge_points": ElecChargePointSampleSerializer(charge_points, many=True).data,
        }
