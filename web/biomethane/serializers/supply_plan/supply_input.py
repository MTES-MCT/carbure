from rest_framework import serializers

from biomethane.models import BiomethaneSupplyInput, BiomethaneSupplyPlan
from biomethane.serializers.fields import DepartmentField, EuropeanFloatField, LabelChoiceField
from biomethane.services.supply_plan import apply_feedstock_field_rules
from core.models import MatierePremiere, Pays
from core.serializers import CountrySerializer
from feedstocks.serializers.feedstock_classification import FeedStockClassificationSerializer


class BiomethaneSupplyInputSerializer(serializers.ModelSerializer):
    origin_country = CountrySerializer()
    feedstock = FeedStockClassificationSerializer()

    class Meta:
        model = BiomethaneSupplyInput
        fields = "__all__"


class BiomethaneSupplyInputCreateSerializer(serializers.ModelSerializer):
    # Use custom choice fields that accept both values and labels
    source = LabelChoiceField(choices=BiomethaneSupplyInput.SOURCE_CHOICES, required=False, allow_null=True)
    material_unit = LabelChoiceField(choices=BiomethaneSupplyInput.MATERIAL_UNIT_CHOICES, required=False, allow_null=True)
    type_cive = LabelChoiceField(choices=BiomethaneSupplyInput.TYPE_CIVE_CHOICES, required=False, allow_null=True)
    culture_details = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    collection_type = LabelChoiceField(
        choices=BiomethaneSupplyInput.COLLECTION_TYPE_CHOICES, required=False, allow_null=True
    )

    feedstock = serializers.SlugRelatedField(slug_field="name", queryset=MatierePremiere.biomethane.all())
    origin_country = serializers.SlugRelatedField(slug_field="code_pays", queryset=Pays.objects.all())

    # Use European float fields for numeric values
    dry_matter_ratio_percent = EuropeanFloatField(required=False, allow_null=True)
    volume = EuropeanFloatField(required=False, allow_null=True)
    average_weighted_distance_km = EuropeanFloatField(required=False, allow_null=True)
    maximum_distance_km = EuropeanFloatField(required=False, allow_null=True)

    class Meta:
        model = BiomethaneSupplyInput
        exclude = ["supply_plan"]

    def to_representation(self, instance):
        return BiomethaneSupplyInputSerializer(instance).data

    def validate(self, data):
        validated_data = super().validate(data)
        origin_country = validated_data.get("origin_country")

        if origin_country and origin_country.code_pays == "FR":
            required_fields = [
                "average_weighted_distance_km",
                "maximum_distance_km",
                "origin_department",
            ]
            for field in required_fields:
                if not validated_data.get(field):
                    raise serializers.ValidationError({field: "Ce champ est requis si le pays d'origine est France"})

        errors = apply_feedstock_field_rules(validated_data)
        if errors:
            raise serializers.ValidationError(errors)

        return validated_data

    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        # Get or create the supply plan for the entity and year
        supply_plan, _ = BiomethaneSupplyPlan.objects.get_or_create(
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
    origin_department = DepartmentField(max_length=3, required=False, allow_null=True)


class BiomethaneSupplyInputExportSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField(source="supply_plan.year", read_only=True)
    origin_country = serializers.SlugRelatedField(slug_field="name", read_only=True)
    feedstock = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = BiomethaneSupplyInput
        exclude = ["id", "supply_plan"]
