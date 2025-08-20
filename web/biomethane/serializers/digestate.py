from rest_framework import serializers

from biomethane.models import BiomethaneDigestate
from biomethane.models.biomethane_digestate_spreading import BiomethaneDigestateSpreading


class BiomethaneDigestateSpreadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneDigestateSpreading
        fields = [
            "id",
            "digestate",
            "spreading_department",
            "spread_quantity",
            "spread_parcels_area",
        ]


class BiomethaneDigestateSerializer(serializers.ModelSerializer):
    spreadings = BiomethaneDigestateSpreadingSerializer(many=True, read_only=True)

    class Meta:
        model = BiomethaneDigestate
        fields = [
            "id",
            "year",
            "status",
            "raw_digestate_tonnage_produced",
            "raw_digestate_dry_matter_rate",
            "solid_digestate_tonnage",
            "liquid_digestate_quantity",
            "average_spreading_valorization_distance",
            "composting_on_site",
            "composting_external_platform",
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
            "spreadings",
        ]
