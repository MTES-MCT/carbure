from rest_framework import serializers

from elec.models import ElecMeter


class ElecMeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecMeter
        fields = "__all__"
