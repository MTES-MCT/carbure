from django.db.models.fields.related import ForeignObjectRel

from biomethane.models import (
    BiomethaneContract,
    BiomethaneDigestate,
    BiomethaneEnergy,
    BiomethaneInjectionSite,
    BiomethaneProductionUnit,
    BiomethaneSupplyPlan,
)

MODEL_BY_KEY = {
    "digestate": BiomethaneDigestate,
    "energy": BiomethaneEnergy,
    "supply_plan": BiomethaneSupplyPlan,
    "contract": BiomethaneContract,
    "production": BiomethaneProductionUnit,
    "injection": BiomethaneInjectionSite,
}


def get_verbose_fields_for_model(model):
    verbose_fields = {}

    for field in model._meta.get_fields():
        if isinstance(field, ForeignObjectRel):
            continue

        field_name = getattr(field, "name", None)
        explicit_verbose_name = getattr(field, "_verbose_name", None)

        if not field_name or explicit_verbose_name is None:
            continue

        verbose_name = str(explicit_verbose_name)

        verbose_fields[field_name] = verbose_name

    return verbose_fields


def get_verbose_fields_by_model():
    return {key: get_verbose_fields_for_model(model) for key, model in MODEL_BY_KEY.items()}


def build_field_metadata_response_schema():
    metadata = get_verbose_fields_by_model()
    properties = {}

    for model_key, fields in metadata.items():
        model_properties = {}
        for field_name, verbose_name in fields.items():
            model_properties[field_name] = {
                "type": "string",
                "enum": [verbose_name],
            }

        properties[model_key] = {
            "type": "object",
            "properties": model_properties,
            "required": sorted(model_properties.keys()),
        }

    return {
        "type": "object",
        "properties": properties,
        "required": sorted(properties.keys()),
    }
