from django.utils.translation import gettext as _
from rest_framework import serializers

from biomethane.models import BiomethaneDigestate
from biomethane.serializers.digestate.spreading import BiomethaneDigestateSpreadingSerializer


class BaseBiomethaneDigestateSerializer(serializers.ModelSerializer):
    composting_locations = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneDigestate.COMPOSTING_LOCATIONS),
        required=False,
    )

    class Meta:
        model = BiomethaneDigestate
        exclude = ["producer", "year", "status"]


class BiomethaneDigestateSerializer(BaseBiomethaneDigestateSerializer):
    spreadings = BiomethaneDigestateSpreadingSerializer(many=True, read_only=True)

    class Meta(BaseBiomethaneDigestateSerializer.Meta):
        exclude = []


class BiomethaneDigestateInputSerializer(BaseBiomethaneDigestateSerializer):
    def validate(self, data):
        from biomethane.services import BiomethaneDigestateService

        validated_data = super().validate(data)

        errors = {}

        # Use the service to get the conditional fields rules
        rules = BiomethaneDigestateService.get_conditional_fields_rules(validated_data)
        required_fields = rules["required_fields"]

        # Check that all required fields are present and non-empty
        for field_name in required_fields:
            if not validated_data.get(field_name):
                # Messages personnalisés selon le contexte
                if field_name in [
                    "external_platform_name",
                    "external_platform_digestate_volume",
                    "external_platform_department",
                    "external_platform_municipality",
                ]:
                    errors[field_name] = [_("Ce champ est obligatoire lorsque 'Plateforme externe' est sélectionné.")]
                elif field_name == "on_site_composted_digestate_volume":
                    errors[field_name] = [_("Ce champ est obligatoire lorsque 'Sur site' est sélectionné.")]
                else:
                    errors[field_name] = [_("Ce champ est obligatoire.")]

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data

    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        validated_data["producer"] = entity
        validated_data["year"] = year

        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["status"] = BiomethaneDigestate.PENDING
        return super().update(instance, validated_data)
