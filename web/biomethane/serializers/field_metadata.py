from rest_framework import serializers

from biomethane.services.field_metadata import MODEL_BY_KEY, get_verbose_fields_for_model


def _build_model_field_metadata_serializer(serializer_name, model):
    model_verbose_fields = get_verbose_fields_for_model(model)
    serializer_fields = {
        field_name: serializers.ChoiceField(
            choices=[verbose_name],
            read_only=True,
        )
        for field_name, verbose_name in model_verbose_fields.items()
    }
    return type(serializer_name, (serializers.Serializer,), serializer_fields)


DigestateFieldMetadataSerializer = _build_model_field_metadata_serializer(
    "DigestateFieldMetadataSerializer",
    MODEL_BY_KEY["digestate"],
)
EnergyFieldMetadataSerializer = _build_model_field_metadata_serializer(
    "EnergyFieldMetadataSerializer",
    MODEL_BY_KEY["energy"],
)
SupplyPlanFieldMetadataSerializer = _build_model_field_metadata_serializer(
    "SupplyPlanFieldMetadataSerializer",
    MODEL_BY_KEY["supply_plan"],
)
ContractFieldMetadataSerializer = _build_model_field_metadata_serializer(
    "ContractFieldMetadataSerializer",
    MODEL_BY_KEY["contract"],
)
ProductionFieldMetadataSerializer = _build_model_field_metadata_serializer(
    "ProductionFieldMetadataSerializer",
    MODEL_BY_KEY["production"],
)
InjectionFieldMetadataSerializer = _build_model_field_metadata_serializer(
    "InjectionFieldMetadataSerializer",
    MODEL_BY_KEY["injection"],
)


class FieldMetadataSerializer(serializers.Serializer):
    digestate = DigestateFieldMetadataSerializer()
    energy = EnergyFieldMetadataSerializer()
    supply_plan = SupplyPlanFieldMetadataSerializer()
    contract = ContractFieldMetadataSerializer()
    production = ProductionFieldMetadataSerializer()
    injection = InjectionFieldMetadataSerializer()
