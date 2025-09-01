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


class BiomethaneDigestateInputSerializer(BaseBiomethaneDigestateSerializer):
    composting_locations = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneDigestate.COMPOSTING_LOCATIONS),
        required=False,
    )

    def validate(self, data):
        errors = {}

        # Always set status to PENDING on update and creation by default
        data["status"] = self.instance.PENDING

        ## Compostage
        if data.get("composting_locations"):
            # If composting_locations contains EXTERNAL_PLATFORM, the related fields are required
            if BiomethaneDigestate.EXTERNAL_PLATFORM in data["composting_locations"]:
                external_platform_fields = [
                    ("external_platform_name", "external_platform_name"),
                    ("external_platform_digestate_volume", "external_platform_digestate_volume"),
                    ("external_platform_department", "external_platform_department"),
                    ("external_platform_municipality", "external_platform_municipality"),
                ]

                for field_name, error_field in external_platform_fields:
                    if not data.get(field_name):
                        errors[error_field] = ["Ce champ est obligatoire lorsque 'Plateforme externe' est sélectionné."]

            # If composting_locations contains ON_SITE, the related field is required
            if BiomethaneDigestate.ON_SITE in data["composting_locations"]:
                if not data.get("on_site_composted_digestate_volume"):
                    errors["on_site_composted_digestate_volume"] = [
                        "Ce champ est obligatoire lorsque 'Sur site' est sélectionné."
                    ]

        if errors:
            raise serializers.ValidationError(errors)

        return data

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
