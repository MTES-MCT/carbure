from rest_framework import serializers
from core.serializers import EntityPreviewSerializer
from elec.models import ElecMeterReadingApplication
from django.contrib.auth import get_user_model


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
    application_date = serializers.DateTimeField(source="created_at")
    charge_point_count = serializers.SerializerMethodField()
    energy_total = serializers.SerializerMethodField()

    def get_charge_point_count(self, instance):
        return instance.charge_point_count

    def get_energy_total(self, instance):
        return round(instance.energy_total, 2)


class ElecMeterReadingApplicationDetailsSerializer(ElecMeterReadingApplicationSerializer):
    email_contacts = serializers.SerializerMethodField()

    class Meta:
        model = ElecMeterReadingApplication
        fields = ElecMeterReadingApplicationSerializer.Meta.fields + ["email_contacts"]

    def get_email_contacts(self, instance):
        user_model = get_user_model()
        users = user_model.objects.filter(userrights__entity__id=instance.cpo.id, userrights__role="ADMIN")
        return [u.email for u in users]
