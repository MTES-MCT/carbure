from rest_framework import serializers

from tiruert.models import MacFossilFuel


class MacFossilFuelSerializer(serializers.ModelSerializer):
    fuel = serializers.CharField(source="fuel.nomenclature")
    operator = serializers.CharField(source="operator.name")
    depot = serializers.CharField(source="depot.name", allow_null=True)

    class Meta:
        model = MacFossilFuel
        fields = [
            "id",
            "fuel",
            "operator",
            "volume",
            "period",
            "year",
            "depot",
            "start_date",
            "end_date",
        ]
