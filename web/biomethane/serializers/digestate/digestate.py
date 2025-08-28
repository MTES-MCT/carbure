from rest_framework import serializers

from biomethane.models import BiomethaneDigestate
from biomethane.serializers.digestate.spreading import BiomethaneDigestateSpreadingSerializer


class BaseBiomethaneDigestateSerializer(serializers.ModelSerializer):
    composting_locations = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneDigestate.COMPOSTING_LOCATIONS),
        read_only=True,
    )

    class Meta:
        model = BiomethaneDigestate
        fields = [
            "id",
            "raw_digestate_tonnage_produced",
            "raw_digestate_dry_matter_rate",
            "solid_digestate_tonnage",
            "liquid_digestate_quantity",
            "average_spreading_valorization_distance",
            "composting_locations",
            "external_platform_name",
            "external_platform_digestate_volume",
            "external_platform_department",
            "external_platform_municipality",
            "on_site_composted_digestate_volume",
            "annual_eliminated_volume",
            "incinerator_landfill_center_name",
            "wwtp_materials_to_incineration",
            "acquiring_companies",
            "sold_volume",
        ]


class BiomethaneDigestateSerializer(BaseBiomethaneDigestateSerializer):
    class Meta(BaseBiomethaneDigestateSerializer.Meta):
        fields = BaseBiomethaneDigestateSerializer.Meta.fields + ["year", "status", "spreadings"]

    spreadings = BiomethaneDigestateSpreadingSerializer(many=True, read_only=True)


class BiomethaneDigestatePatchSerializer(BaseBiomethaneDigestateSerializer):
    def update(self, instance, validated_data):
        validated_data["status"] = BiomethaneDigestate.PENDING
        return super().update(instance, validated_data)


class BiomethaneDigestateAddSerializer(BaseBiomethaneDigestateSerializer):
    composting_locations = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneDigestate.COMPOSTING_LOCATIONS),
        required=False,
    )

    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        if not entity:
            raise serializers.ValidationError({"entity": ["Entité manquante."]})

        if BiomethaneDigestate.objects.filter(producer=entity, year=year).exists():
            raise serializers.ValidationError({"producer": ["Un digestat existe déjà pour cette entité."]})

        validated_data["producer"] = entity
        validated_data["year"] = year

        return super().create(validated_data)
