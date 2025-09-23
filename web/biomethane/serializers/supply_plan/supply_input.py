from rest_framework import serializers

from biomethane.models import BiomethaneSupplyInput


class BiomethaneSupplyInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneSupplyInput
        fields = "__all__"


class BiomethaneSupplyInputCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneSupplyInput
        exclude = ["supply_plan"]

    def to_representation(self, instance):
        return BiomethaneSupplyInputSerializer(instance).data

    def validate(self, data):
        validated_data = super().validate(data)

        material_unit = validated_data.get("material_unit")
        dry_matter_ratio_percent = validated_data.get("dry_matter_ratio_percent")

        # Check consistency between material_unit and dry_matter_ratio_percent
        if material_unit == BiomethaneSupplyInput.DRY and dry_matter_ratio_percent is None:
            raise serializers.ValidationError(
                {"dry_matter_ratio_percent": "Le ratio de matière sèche est requis pour l'unité 'Sèche'"}
            )

        if material_unit == BiomethaneSupplyInput.WET and dry_matter_ratio_percent is not None:
            raise serializers.ValidationError(
                {"dry_matter_ratio_percent": "Le ratio de matière sèche ne doit pas être renseigné pour l'unité 'Brute'"}
            )

        return validated_data
