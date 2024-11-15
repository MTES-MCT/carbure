from rest_framework import serializers

from core.models import Depot


class DepotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depot
        fields = [
            "depot_id",
            "name",
            "city",
            "country",
            "depot_type",
            "address",
            "postal_code",
            "electrical_efficiency",
            "thermal_efficiency",
            "useful_temperature",
        ]
