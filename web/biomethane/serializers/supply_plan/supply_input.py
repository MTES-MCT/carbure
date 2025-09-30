from rest_framework import serializers

from biomethane.models import BiomethaneSupplyInput, BiomethaneSupplyPlan
from biomethane.serializers.fields import DepartmentField, EuropeanFloatField, LabelChoiceField
from biomethane.utils import get_declaration_period
from core.models import Pays


class BiomethaneSupplyInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneSupplyInput
        fields = "__all__"


class BiomethaneSupplyInputCreateSerializer(serializers.ModelSerializer):
    # Use custom choice fields that accept both values and labels
    source = LabelChoiceField(choices=BiomethaneSupplyInput.SOURCE_CHOICES)
    crop_type = LabelChoiceField(choices=BiomethaneSupplyInput.CROP_TYPE_CHOICES)
    input_category = LabelChoiceField(choices=BiomethaneSupplyInput.INPUT_CATEGORY_CHOICES)
    material_unit = LabelChoiceField(choices=BiomethaneSupplyInput.MATERIAL_UNIT_CHOICES)

    # Use European float fields for numeric values
    dry_matter_ratio_percent = EuropeanFloatField(required=False, allow_null=True)
    volume = EuropeanFloatField()
    average_weighted_distance_km = EuropeanFloatField(required=False, allow_null=True)
    maximum_distance_km = EuropeanFloatField(required=False, allow_null=True)

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

    def create(self, validated_data):
        entity = self.context.get("entity")
        year = get_declaration_period()

        # Get or create the supply plan for the entity and year
        supply_plan, created = BiomethaneSupplyPlan.objects.get_or_create(
            producer=entity,
            year=year,
            defaults={},
        )

        if isinstance(validated_data, list):
            # Handle bulk creation (many=True) - for Excel import
            instances = []

            for item in validated_data:
                item["supply_plan"] = supply_plan
                instances.append(BiomethaneSupplyInput(**item))

            return BiomethaneSupplyInput.objects.bulk_create(instances)
        else:
            # Handle single creation - for API calls
            validated_data["supply_plan"] = supply_plan
            return BiomethaneSupplyInput.objects.create(**validated_data)


class BiomethaneSupplyInputCreateFromExcelSerializer(BiomethaneSupplyInputCreateSerializer):
    # Override some fields to handle Excel-specific formats
    origin_country = serializers.SlugRelatedField(slug_field="name", queryset=Pays.objects.all())
    origin_department = DepartmentField(max_length=3)
