from rest_framework import serializers

from transactions.models import Depot


class DepotResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depot
        fields = [
            "id",
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
