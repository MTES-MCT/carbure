from rest_framework import serializers

from elec.models import ElecMeter


class ElecMeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecMeter
        fields = [
            "id",
            "mid_certificate",
            "initial_index",
            "initial_index_date",
            "charge_point",
        ]
