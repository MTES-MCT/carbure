from rest_framework import serializers

from tiruert.models import FossilFuel, MacFossilFuel


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


class MacFossilFuelInputSerializer(serializers.Serializer):
    fuel = serializers.SlugRelatedField(slug_field="nomenclature", queryset=FossilFuel.objects.all())
    month = serializers.IntegerField(min_value=1, max_value=12)
    volume = serializers.FloatField(min_value=0)
