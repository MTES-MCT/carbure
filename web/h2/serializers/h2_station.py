from rest_framework import serializers

from core.models.geography import Pays
from h2.models import H2Station
from transactions.models.site import Site


class H2StationSerializer(serializers.ModelSerializer):
    distributed_pressure = serializers.ListField(
        child=serializers.ChoiceField(choices=H2Station.DISTRIBUTION_PRESSURES),
    )
    entity_name = serializers.CharField(source="created_by.name", read_only=True, allow_null=True)

    class Meta:
        model = H2Station
        fields = [
            "id",
            "entity_name",
            "name",
            "site_siret",
            "address",
            "postal_code",
            "city",
            "commissioning_date",
            "access_type",
            "distributed_pressure",
            "has_personal_vehicle_connector",
            "has_compliant_measuring_instruments",
            "storage_capacity",
            "distribution_capacity",
        ]


class H2StationInputSerializer(serializers.ModelSerializer):
    distributed_pressure = serializers.ListField(
        child=serializers.ChoiceField(choices=H2Station.DISTRIBUTION_PRESSURES),
    )

    class Meta:
        model = H2Station
        exclude = ["private", "is_enabled", "created_by", "site_type"]

    def create(self, validated_data):
        entity = self.context.get("entity")
        validated_data["created_by"] = entity
        validated_data["site_type"] = Site.H2_REFUELING_STATION
        validated_data["country"] = Pays.objects.get(code_pays="FR")
        return super().create(validated_data)
