from importlib.util import find_spec

from django.apps import apps
from django.db.models.fields.related import ForeignObjectRel


def get_verbose_fields_for_model(model):
    verbose_fields = {}

    for field in model._meta.get_fields():
        if isinstance(field, ForeignObjectRel):
            continue

        field_name = getattr(field, "name", None)
        explicit_verbose_name = getattr(field, "_verbose_name", None)

        if not field_name or explicit_verbose_name is None:
            continue

        verbose_fields[field_name] = str(explicit_verbose_name)

    return verbose_fields


def get_verbose_fields_by_model_for_module(module_name):
    app_config = _resolve_app_config(module_name)
    if not _has_models_package(app_config.name):
        return {}

    verbose_fields_by_model = {}
    for model in app_config.get_models():
        fields = get_verbose_fields_for_model(model)
        if fields:
            verbose_fields_by_model[model._meta.model_name] = fields

    return verbose_fields_by_model


def get_verbose_fields_for_translation(module_names):
    translation_fields = {}

    for module_name in module_names:
        module_key = module_name.strip()
        if not module_key:
            continue

        model_fields = get_verbose_fields_by_model_for_module(module_key)
        for model_name, fields in model_fields.items():
            for field_name, verbose_name in fields.items():
                translation_key = f"{module_key}.{model_name}.{field_name}"
                translation_fields[translation_key] = verbose_name

    return translation_fields


def _resolve_app_config(module_name):
    try:
        return apps.get_app_config(module_name)
    except LookupError:
        for app_config in apps.get_app_configs():
            if app_config.name == module_name:
                return app_config

    raise LookupError(f"Unknown Django app module: {module_name}")


def _has_models_package(module_name):
    models_spec = find_spec(f"{module_name}.models")
    return bool(models_spec and models_spec.submodule_search_locations)
